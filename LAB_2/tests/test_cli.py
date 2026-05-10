"""Тесты консольного интерфейса."""

import builtins

from infrastructure.cli import Lab2Cli


class StubService:
    """Небольшая заглушка сервиса вместо реального вычисления."""

    def __init__(self, study_result) -> None:
        self.study_result = study_result
        self.calls: list[str] = []

    def study_function(self, expression_text: str):
        """Запоминает запрос и возвращает заранее подготовленный ответ."""
        self.calls.append(expression_text)
        return self.study_result


class StubPrinter:
    """Заглушка форматтера, возвращающая фиксированный текст."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.calls: list[object] = []

    def format(self, study_result) -> str:
        """Запоминает объект отчета и отдает готовую строку."""
        self.calls.append(study_result)
        return self.text


def test_cli_runs_analysis_and_exit(monkeypatch) -> None:
    """Проверяет новый сценарий: сразу ввод функции, вывод отчета и завершение."""
    study_result = object()
    service = StubService(study_result)
    report_printer = StubPrinter("REPORT")
    entered_values = iter(["a&b"])
    printed_texts: list[str] = []

    monkeypatch.setattr(builtins, "input", lambda _: next(entered_values))
    monkeypatch.setattr(builtins, "print", lambda text="": printed_texts.append(text))

    Lab2Cli(service=service, report_printer=report_printer).run()

    assert service.calls == ["a&b"]
    assert report_printer.calls == [study_result]
    assert "REPORT" in printed_texts


def test_cli_repeats_input_after_error(monkeypatch) -> None:
    """Проверяет, что после ошибки программа повторно ждет выражение."""
    study_result = object()
    report_printer = StubPrinter("REPORT")
    printed_texts: list[str] = []

    class FlakyService:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def study_function(self, expression_text: str):
            self.calls.append(expression_text)
            if len(self.calls) == 1:
                raise ValueError("bad expression")
            return study_result

    service = FlakyService()
    entered_values = iter(["bad", "a|b"])
    monkeypatch.setattr(builtins, "input", lambda _: next(entered_values))
    monkeypatch.setattr(builtins, "print", lambda text="": printed_texts.append(text))

    Lab2Cli(service=service, report_printer=report_printer).run()

    assert service.calls == ["bad", "a|b"]
    assert "Ошибка разбора: bad expression" in printed_texts
    assert "Повторите ввод выражения." in printed_texts
    assert "REPORT" in printed_texts
