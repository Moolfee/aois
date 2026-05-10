"""Консольный интерфейс программы.

В новой версии запуска пользователь не выбирает пункт меню.
Программа сразу ждет логическую функцию, а если выражение некорректно,
сообщает об ошибке и снова просит ввод.
"""

from application.lab2_service import Lab2Service
from domain.errors import Lab2Error
from infrastructure.report_printer import StudyReportPrinter


class Lab2Cli:
    """Прямой консольный режим анализа логической функции."""

    def __init__(
        self,
        service: Lab2Service | None = None,
        report_printer: StudyReportPrinter | None = None,
    ) -> None:
        """Сохраняет прикладной сервис и форматтер итогового отчета."""
        self._service = service or Lab2Service()
        self._report_printer = report_printer or StudyReportPrinter()

    def run(self) -> None:
        """Ждет корректную функцию, после чего печатает отчет и завершает работу."""
        while True:
            try:
                expression_text = self._read_expression()
                study_result = self._service.study_function(expression_text)
            except (ValueError, Lab2Error) as error:
                self._show_error(error)
                continue
            print(self._report_printer.format(study_result))
            return

    def _read_expression(self) -> str:
        """Запрашивает у пользователя одну логическую функцию."""
        return input("Введите логическую функцию: ").strip()

    def _show_error(self, error: Lab2Error | ValueError) -> None:
        """Единообразно выводит ошибку и подсказывает, что ввод можно повторить."""
        print(f"Ошибка разбора: {error}")
        print("Повторите ввод выражения.")
