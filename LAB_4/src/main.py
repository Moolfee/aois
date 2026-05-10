"""Точка входа в программу."""

from infrastructure.cli import Cli


def main() -> None:
    """Запускает консольный интерфейс хеш-таблицы."""
    cli = Cli()
    cli.run()


if __name__ == "__main__":
    main()
