"""Пользовательские исключения."""

import sys


class Error(Exception):
    """Базовый класс для осмысленных ошибок лабораторной."""


class HashTableError(Error):
    """Общая ошибка работы с хеш-таблицей."""


class InvalidCapacityError(HashTableError):
    """Размер таблицы задан некорректно."""


class EmptyKeyError(HashTableError):
    """Ключ не может быть пустым."""


class KeyAlreadyExistsError(HashTableError):
    """Элемент с таким ключом уже есть в таблице."""


class KeyNotFoundError(HashTableError):
    """Элемент с таким ключом не найден."""


sys.modules.setdefault("src.domain.errors", sys.modules[__name__])
