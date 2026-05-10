"""Консольный интерфейс."""

import sys

from application.service import Service
from domain.errors import Error
from infrastructure.table_printer import HashTablePrinter


class Cli:
    """Меню для ручной работы с хеш-таблицей."""

    def __init__(
        self,
        service: Service | None = None,
        printer: HashTablePrinter | None = None,
    ) -> None:
        """Сохраняет сервис и форматтер таблицы."""
        self._service = service or Service()
        self._printer = printer or HashTablePrinter()

    def run(self) -> None:
        """Запускает интерактивный режим."""
        while True:
            self._print_menu()
            choice = input("Выберите пункт: ").strip()
            if choice == "0":
                print("Выход.")
                return
            try:
                self._handle_choice(choice)
            except (ValueError, Error) as error:
                print(f"Ошибка: {error}")

    @staticmethod
    def _print_menu() -> None:
        print("\n===== МЕНЮ =====")
        print("1. Создать запись")
        print("2. Прочитать запись")
        print("3. Обновить запись")
        print("4. Удалить запись")
        print("5. Показать таблицу")
        print("0. Выход")

    def _handle_choice(self, choice: str) -> None:
        handlers = {
            "1": self._create,
            "2": self._read,
            "3": self._update,
            "4": self._delete,
            "5": self._show_table,
        }
        handler = handlers.get(choice)
        if handler is None:
            raise ValueError("неизвестный пункт меню")
        handler()

    @staticmethod
    def _read_key() -> str:
        return input("Введите ключ: ").strip()

    @staticmethod
    def _read_value() -> str:
        return input("Введите значение: ").strip()

    def _create(self) -> None:
        entry = self._service.create(self._read_key(), self._read_value())
        print(f"Создано: {entry.key}: {entry.value}")

    def _read(self) -> None:
        key = self._read_key()
        print(f"Значение: {self._service.read(key)}")

    def _update(self) -> None:
        entry = self._service.update(self._read_key(), self._read_value())
        print(f"Обновлено: {entry.key}: {entry.value}")

    def _delete(self) -> None:
        entry = self._service.delete(self._read_key())
        print(f"Удалено: {entry.key}: {entry.value}")

    def _show_table(self) -> None:
        print(self._printer.format(self._service.snapshot()))


sys.modules.setdefault("src.infrastructure.cli", sys.modules[__name__])
