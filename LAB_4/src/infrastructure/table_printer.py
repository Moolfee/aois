"""Форматирование состояния хеш-таблицы для консоли."""

import sys

from domain.entities import HashTableSnapshot


class HashTablePrinter:
    """Преобразует снимок таблицы в текстовый отчет."""

    def format(self, snapshot: HashTableSnapshot) -> str:
        """Возвращает удобное представление корзин и цепочек-деревьев."""
        lines = [
            "=== ХЕШ-ТАБЛИЦА ===",
            f"Размер: {snapshot.capacity}",
            f"Записей: {snapshot.size}",
            f"Коэффициент заполнения: {snapshot.load_factor:.2f}",
            "",
            "Корзины:",
        ]
        for bucket in snapshot.buckets:
            if bucket.entries:
                values = " -> ".join(
                    f"{entry.key}: {entry.value}" for entry in bucket.entries
                )
            else:
                values = "-"
            lines.append(f"{bucket.index:>3}: {values}")
        return "\n".join(lines)


sys.modules.setdefault("src.infrastructure.table_printer", sys.modules[__name__])
