"""Реализация хеш-таблицы с CRUD-операциями."""

import sys
from dataclasses import dataclass
from typing import Any

from domain.entities import BucketSnapshot, HashEntry, HashTableSnapshot
from domain.errors import (
    EmptyKeyError,
    InvalidCapacityError,
    KeyAlreadyExistsError,
    KeyNotFoundError,
)
from domain.hash_function import DivisionHashFunction


@dataclass
class _TreeNode:
    """Узел AVL-дерева внутри одной корзины."""

    entry: HashEntry
    height: int = 1
    left: "_TreeNode | None" = None
    right: "_TreeNode | None" = None


class _AvlBucket:
    """Сбалансированная цепочка записей одной корзины."""

    def __init__(self) -> None:
        self._root: _TreeNode | None = None

    def insert(self, entry: HashEntry) -> None:
        """Добавляет запись в дерево."""
        self._root = self._insert(self._root, entry)

    def read(self, key: str) -> HashEntry | None:
        """Ищет запись по ключу."""
        node = self._root
        while node is not None:
            if key == node.entry.key:
                return node.entry
            if key < node.entry.key:
                node = node.left
            else:
                node = node.right
        return None

    def update(self, entry: HashEntry) -> bool:
        """Заменяет значение существующей записи."""
        node = self._root
        while node is not None:
            if entry.key == node.entry.key:
                node.entry = entry
                return True
            if entry.key < node.entry.key:
                node = node.left
            else:
                node = node.right
        return False

    def delete(self, key: str) -> HashEntry | None:
        """Удаляет запись по ключу."""
        self._root, deleted = self._delete(self._root, key)
        return deleted

    def contains(self, key: str) -> bool:
        """Проверяет наличие ключа."""
        return self.read(key) is not None

    def entries(self) -> tuple[HashEntry, ...]:
        """Возвращает записи в порядке возрастания ключей."""
        result: list[HashEntry] = []
        self._traverse_in_order(self._root, result)
        return tuple(result)

    def _insert(self, node: _TreeNode | None, entry: HashEntry) -> _TreeNode:
        if node is None:
            return _TreeNode(entry=entry)
        if entry.key == node.entry.key:
            raise KeyAlreadyExistsError(f"ключ '{entry.key}' уже существует")
        if entry.key < node.entry.key:
            node.left = self._insert(node.left, entry)
        else:
            node.right = self._insert(node.right, entry)
        return self._rebalance(node)

    def _delete(
        self,
        node: _TreeNode | None,
        key: str,
    ) -> tuple[_TreeNode | None, HashEntry | None]:
        if node is None:
            return None, None
        if key < node.entry.key:
            node.left, deleted = self._delete(node.left, key)
        elif key > node.entry.key:
            node.right, deleted = self._delete(node.right, key)
        else:
            deleted = node.entry
            if node.left is None:
                return node.right, deleted
            if node.right is None:
                return node.left, deleted
            successor = self._min_node(node.right)
            node.entry = successor.entry
            node.right, _ = self._delete(node.right, successor.entry.key)
        return self._rebalance(node), deleted

    def _rebalance(self, node: _TreeNode) -> _TreeNode:
        self._update_height(node)
        balance = self._balance_factor(node)
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def _rotate_left(self, node: _TreeNode) -> _TreeNode:
        pivot = node.right
        if pivot is None:
            return node
        node.right = pivot.left
        pivot.left = node
        self._update_height(node)
        self._update_height(pivot)
        return pivot

    def _rotate_right(self, node: _TreeNode) -> _TreeNode:
        pivot = node.left
        if pivot is None:
            return node
        node.left = pivot.right
        pivot.right = node
        self._update_height(node)
        self._update_height(pivot)
        return pivot

    def _min_node(self, node: _TreeNode) -> _TreeNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _traverse_in_order(
        self,
        node: _TreeNode | None,
        result: list[HashEntry],
    ) -> None:
        if node is None:
            return
        self._traverse_in_order(node.left, result)
        result.append(node.entry)
        self._traverse_in_order(node.right, result)

    def _height(self, node: _TreeNode | None) -> int:
        return node.height if node is not None else 0

    def _update_height(self, node: _TreeNode) -> None:
        node.height = max(self._height(node.left), self._height(node.right)) + 1

    def _balance_factor(self, node: _TreeNode | None) -> int:
        if node is None:
            return 0
        return self._height(node.left) - self._height(node.right)


class HashTable:
    """Ассоциативная таблица с цепочками на сбалансированных деревьях."""

    _DEFAULT_CAPACITY = 11
    _MAX_LOAD_FACTOR = 0.75

    def __init__(
        self,
        capacity: int = _DEFAULT_CAPACITY,
        hash_function: DivisionHashFunction | None = None,
    ) -> None:
        """Создает таблицу с заданным числом корзин."""
        if capacity <= 0:
            raise InvalidCapacityError("размер хеш-таблицы должен быть положительным")
        self._hash_function = hash_function or DivisionHashFunction()
        self._buckets: list[_AvlBucket] = [_AvlBucket() for _ in range(capacity)]
        self._size = 0

    @property
    def capacity(self) -> int:
        """Текущий размер массива корзин."""
        return len(self._buckets)

    @property
    def size(self) -> int:
        """Количество записей в таблице."""
        return self._size

    @property
    def load_factor(self) -> float:
        """Коэффициент заполнения таблицы."""
        return self._size / self.capacity

    def create(self, key: str, value: Any) -> HashEntry:
        """Добавляет новую запись."""
        entry = HashEntry(self._normalize_key(key), value)
        bucket = self._bucket_for(entry.key)
        bucket.insert(entry)
        self._size += 1
        if self.load_factor > self._MAX_LOAD_FACTOR:
            self._resize(self.capacity * 2 + 1)
        return entry

    def read(self, key: str) -> Any:
        """Возвращает значение по ключу."""
        normalized_key = self._normalize_key(key)
        entry = self._bucket_for(normalized_key).read(normalized_key)
        if entry is None:
            raise KeyNotFoundError(f"ключ '{key}' не найден")
        return entry.value

    def update(self, key: str, value: Any) -> HashEntry:
        """Обновляет значение существующей записи."""
        normalized_key = self._normalize_key(key)
        entry = HashEntry(normalized_key, value)
        if not self._bucket_for(normalized_key).update(entry):
            raise KeyNotFoundError(f"ключ '{key}' не найден")
        return entry

    def delete(self, key: str) -> HashEntry:
        """Удаляет запись по ключу и возвращает удаленный элемент."""
        normalized_key = self._normalize_key(key)
        deleted = self._bucket_for(normalized_key).delete(normalized_key)
        if deleted is None:
            raise KeyNotFoundError(f"ключ '{key}' не найден")
        self._size -= 1
        return deleted

    def contains(self, key: str) -> bool:
        """Проверяет наличие ключа в таблице."""
        normalized_key = self._normalize_key(key)
        return self._bucket_for(normalized_key).contains(normalized_key)

    def snapshot(self) -> HashTableSnapshot:
        """Возвращает неизменяемый снимок текущего состояния."""
        buckets = tuple(
            BucketSnapshot(index=index, entries=bucket.entries())
            for index, bucket in enumerate(self._buckets)
        )
        return HashTableSnapshot(
            capacity=self.capacity,
            size=self.size,
            load_factor=self.load_factor,
            buckets=buckets,
        )

    def _bucket_for(self, key: str) -> _AvlBucket:
        index = self._hash_function.calculate(str(key), self.capacity)
        return self._buckets[index]

    def _normalize_key(self, key: str) -> str:
        normalized_key = str(key).strip()
        if not normalized_key:
            raise EmptyKeyError("ключ не может быть пустым")
        return normalized_key

    def _resize(self, new_capacity: int) -> None:
        entries = [entry for bucket in self._buckets for entry in bucket.entries()]
        self._buckets = [_AvlBucket() for _ in range(new_capacity)]
        self._size = 0
        for entry in entries:
            self._bucket_for(entry.key).insert(entry)
            self._size += 1


sys.modules.setdefault("src.domain.hash_table", sys.modules[__name__])
