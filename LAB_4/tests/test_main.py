"""Тесты точки входа."""

import importlib
import runpy

import application
import application.service
import domain
import domain.entities
import domain.errors
import domain.hash_function
import domain.hash_table
import infrastructure
import infrastructure.cli
import infrastructure.table_printer
import main
import src


def test_package_modules_are_importable() -> None:
    """Проверяет, что пакеты приложения импортируются."""
    assert application.__doc__ == "Прикладной слой."
    assert domain.__doc__ == "Доменный слой."
    assert infrastructure.__doc__ == "Инфраструктурный слой."
    assert src.__doc__ == "Исходный код."


def test_source_modules_are_reloadable() -> None:
    """Проверяет, что модули исходного кода повторно загружаются без ошибок."""
    modules = [
        src,
        application,
        domain,
        infrastructure,
        domain.entities,
        domain.errors,
        domain.hash_function,
        domain.hash_table,
        application.service,
        infrastructure.table_printer,
        infrastructure.cli,
        main,
    ]

    for module in modules:
        importlib.reload(module)


def test_main_creates_and_runs_cli(monkeypatch) -> None:
    """Проверяет, что main запускает консольный интерфейс."""
    calls: list[str] = []

    class FakeCli:
        def run(self) -> None:
            calls.append("run")

    monkeypatch.setattr(main, "Cli", FakeCli)

    main.main()

    assert calls == ["run"]


def test_main_script_entrypoint(monkeypatch) -> None:
    """Проверяет блок запуска файла как скрипта."""
    calls: list[str] = []

    class FakeCli:
        def run(self) -> None:
            calls.append("run")

    monkeypatch.setattr("infrastructure.cli.Cli", FakeCli)

    runpy.run_path("LAB_4/src/main.py", run_name="__main__")

    assert calls == ["run"]
