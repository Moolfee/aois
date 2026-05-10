"""Структуры данных для представления состояния хеш-таблицы."""

import sys
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HashEntry:
    """Одна запись хеш-таблицы."""

    key: str
    value: Any


@dataclass(frozen=True)
class BucketSnapshot:
    """Снимок одной корзины с цепочкой коллизий на дереве."""

    index: int
    entries: tuple[HashEntry, ...]


@dataclass(frozen=True)
class HashTableSnapshot:
    """Полное состояние таблицы, удобное для вывода и тестов."""

    capacity: int
    size: int
    load_factor: float
    buckets: tuple[BucketSnapshot, ...]


sys.modules.setdefault("src.domain.entities", sys.modules[__name__])
