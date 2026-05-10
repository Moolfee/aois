"""Фасад прикладного слоя."""

import sys
from typing import Any

from domain.entities import HashEntry, HashTableSnapshot
from domain.hash_table import HashTable


class Service:
    """Координирует CRUD-операции над хеш-таблицей."""

    def __init__(self, hash_table: HashTable | None = None) -> None:
        """Создает сервис с рабочей таблицей по умолчанию."""
        self._hash_table = hash_table or HashTable()

    def create(self, key: str, value: Any) -> HashEntry:
        """Добавляет новую пару ключ-значение."""
        return self._hash_table.create(key, value)

    def read(self, key: str) -> Any:
        """Читает значение по ключу."""
        return self._hash_table.read(key)

    def update(self, key: str, value: Any) -> HashEntry:
        """Изменяет значение существующего ключа."""
        return self._hash_table.update(key, value)

    def delete(self, key: str) -> HashEntry:
        """Удаляет запись по ключу."""
        return self._hash_table.delete(key)

    def contains(self, key: str) -> bool:
        """Проверяет наличие ключа."""
        return self._hash_table.contains(key)

    def snapshot(self) -> HashTableSnapshot:
        """Возвращает состояние таблицы."""
        return self._hash_table.snapshot()


sys.modules.setdefault("src.application.service", sys.modules[__name__])
