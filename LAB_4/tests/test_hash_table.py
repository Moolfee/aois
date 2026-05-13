"""Тесты хеш-таблицы."""

import pytest

from domain.errors import (
    EmptyKeyError,
    InvalidCapacityError,
    KeyAlreadyExistsError,
    KeyNotFoundError,
)
from domain.hash_table import HashTable
from domain.hash_function import DivisionHashFunction


def test_hash_table_supports_crud_operations() -> None:
    """Проверяет полный цикл создания, чтения, обновления и удаления."""
    table = HashTable(capacity=5)

    created = table.create("alpha", "first")
    assert created.key == "alpha"
    assert table.read("alpha") == "first"

    updated = table.update("alpha", "second")
    assert updated.value == "second"
    assert table.read("alpha") == "second"

    deleted = table.delete("alpha")
    assert deleted.key == "alpha"
    assert table.size == 0
    with pytest.raises(KeyNotFoundError):
        table.read("alpha")


def test_hash_table_keeps_entries_with_collisions() -> None:
    """Проверяет, что цепочки-деревья сохраняют разные ключи в одной корзине."""
    table = HashTable(capacity=1)

    table.create("first", 1)
    table.create("second", 2)

    assert table.read("first") == 1
    assert table.read("second") == 2
    snapshot = table.snapshot()
    filled_buckets = [bucket for bucket in snapshot.buckets if bucket.entries]
    assert len(filled_buckets) == 1
    assert len(filled_buckets[0].entries) == 2


def test_collision_chain_is_balanced_tree() -> None:
    """Проверяет, что цепочка коллизий хранится как сбалансированное дерево."""
    table = HashTable(capacity=11, hash_function=_SingleBucketHashFunction())

    for key in ["a", "b", "c", "d", "e", "f", "g"]:
        table.create(key, key.upper())

    bucket = table._buckets[0]
    entries = bucket.entries()

    assert [entry.key for entry in entries] == ["a", "b", "c", "d", "e", "f", "g"]
    assert bucket._root is not None
    assert bucket._root.height == 3
    assert _is_balanced(bucket._root)


def _is_balanced(node) -> bool:
    if node is None:
        return True
    left_height = node.left.height if node.left is not None else 0
    right_height = node.right.height if node.right is not None else 0
    return (
        abs(left_height - right_height) <= 1
        and _is_balanced(node.left)
        and _is_balanced(node.right)
    )


class _SingleBucketHashFunction:
    def calculate(self, key: str, capacity: int) -> int:
        if not str(key).strip():
            raise EmptyKeyError("ключ не может быть пустым")
        return 0


def test_hash_table_rejects_duplicate_create() -> None:
    """Проверяет, что create не подменяет существующую запись."""
    table = HashTable(capacity=3)

    table.create("key", "value")

    with pytest.raises(KeyAlreadyExistsError):
        table.create("key", "new value")


def test_hash_table_validates_capacity_and_key() -> None:
    """Проверяет базовую валидацию таблицы и ключей."""
    with pytest.raises(InvalidCapacityError):
        HashTable(capacity=0)

    table = HashTable()
    with pytest.raises(EmptyKeyError):
        table.create("   ", "value")

    with pytest.raises(InvalidCapacityError):
        DivisionHashFunction().calculate("key", 0)


def test_hash_table_resizes_after_high_load() -> None:
    """Проверяет автоматическое расширение при большом заполнении."""
    table = HashTable(capacity=3)

    table.create("a", 1)
    table.create("b", 2)
    table.create("c", 3)

    assert table.capacity == 7
    assert table.read("a") == 1
    assert table.read("b") == 2
    assert table.read("c") == 3


def test_avl_bucket_handles_left_branches_and_right_rotation() -> None:
    """Проверяет вставку влево, правое вращение и поиск слева."""
    table = HashTable(capacity=11, hash_function=_SingleBucketHashFunction())

    for key in ["g", "f", "e", "d", "c", "b", "a"]:
        table.create(key, key.upper())

    bucket = table._buckets[0]

    assert [entry.key for entry in bucket.entries()] == ["a", "b", "c", "d", "e", "f", "g"]
    assert table.read("a") == "A"
    assert bucket._root is not None
    assert _is_balanced(bucket._root)


def test_avl_bucket_deletes_node_with_two_children() -> None:
    """Проверяет ветку удаления узла с преемником справа."""
    table = HashTable(capacity=11, hash_function=_SingleBucketHashFunction())

    for key in ["d", "b", "f", "a", "c", "e", "g"]:
        table.create(key, key.upper())

    deleted = table.delete("d")
    bucket = table._buckets[0]

    assert deleted.key == "d"
    assert [entry.key for entry in bucket.entries()] == ["a", "b", "c", "e", "f", "g"]
    assert bucket._root is not None
    assert bucket._root.entry.key == "e"
    assert _is_balanced(bucket._root)


def test_hash_table_contains_update_and_delete_missing_paths() -> None:
    """Проверяет отсутствующие ключи и обновление в ветвях дерева."""
    table = HashTable(capacity=11, hash_function=_SingleBucketHashFunction())

    for key in ["m", "c", "t"]:
        table.create(key, key)

    assert table.contains("c") is True
    assert table.contains("a") is False
    assert table.update("c", "changed").value == "changed"
    assert table.read("c") == "changed"

    with pytest.raises(KeyNotFoundError):
        table.update("z", "missing")

    with pytest.raises(KeyNotFoundError):
        table.delete("z")
