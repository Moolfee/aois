"""Хеш-функция.

В задании хеш-функция отсылает к лабораторной 6. В текущем дереве проекта
ее реализации нет, поэтому здесь явно выделена учебная функция деления:
сначала ключ переводится в числовой код, затем берется остаток по размеру
таблицы: `h(k) = code(k) mod m`.
"""

import sys

from domain.errors import EmptyKeyError, InvalidCapacityError


class DivisionHashFunction:
    """Преобразует строковый ключ в индекс таблицы методом деления."""

    _POLYNOMIAL_BASE = 31

    def calculate(self, key: str, capacity: int) -> int:
        """Возвращает индекс корзины для ключа."""
        if capacity <= 0:
            raise InvalidCapacityError("размер хеш-таблицы должен быть положительным")
        normalized_key = self._normalize_key(key)
        return self._to_numeric_code(normalized_key) % capacity

    def _normalize_key(self, key: str) -> str:
        """Проверяет и нормализует ключ перед хешированием."""
        normalized_key = str(key).strip()
        if not normalized_key:
            raise EmptyKeyError("ключ не может быть пустым")
        return normalized_key

    def _to_numeric_code(self, key: str) -> int:
        """Переводит строку в числовой код полиномиальным накоплением."""
        code = 0
        for symbol in key:
            code = code * self._POLYNOMIAL_BASE + ord(symbol)
        return code


sys.modules.setdefault("src.domain.hash_function", sys.modules[__name__])
