"""Тесты консольного интерфейса."""

import builtins

from infrastructure.cli import Cli


def test_cli_runs_user_scenario(monkeypatch, capsys) -> None:
    """Проверяет основные пункты меню через имитацию пользовательского ввода."""
    inputs = iter(
        [
            "1",
            "name",
            "Ada",
            "2",
            "name",
            "3",
            "name",
            "Grace",
            "5",
            "4",
            "name",
            "2",
            "name",
            "9",
            "0",
        ]
    )
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    Cli().run()

    output = capsys.readouterr().out
    assert "Создано: name: Ada" in output
    assert "Значение: Ada" in output
    assert "Обновлено: name: Grace" in output
    assert "=== ХЕШ-ТАБЛИЦА ===" in output
    assert "Удалено: name: Grace" in output
    assert "Ошибка: ключ 'name' не найден" in output
    assert "Ошибка: неизвестный пункт меню" in output
    assert "Выход." in output
