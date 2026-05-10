"""Тесты прикладного сервиса и форматтера."""

from application.service import Service
from infrastructure.table_printer import HashTablePrinter


def test_service_wraps_hash_table_operations() -> None:
    """Проверяет основные операции через фасад лабораторной."""
    service = Service()

    service.create("name", "Ada")
    assert service.contains("name")
    assert service.read("name") == "Ada"

    service.update("name", "Grace")
    assert service.read("name") == "Grace"

    service.delete("name")
    assert not service.contains("name")


def test_printer_contains_table_state() -> None:
    """Проверяет, что отчет показывает основные параметры таблицы."""
    service = Service()
    service.create("one", "1")

    text = HashTablePrinter().format(service.snapshot())

    assert "=== ХЕШ-ТАБЛИЦА ===" in text
    assert "Размер:" in text
    assert "Записей: 1" in text
    assert "one: 1" in text
