"""Тесты вспомогательных анализаторов и точки входа."""

import importlib
import runpy

from domain.post_family import PostCriterionInspector
from domain.redundant_variable_finder import RedundantVariableInspector
from domain.zhegalkin_transform import PolynomialComposer
from domain.truth_matrix import TruthMatrixComposer
import main


def test_post_and_redundant_helpers_cover_negative_branches() -> None:
    """Проверяет немонотонную функцию и фиктивную переменную."""
    _, xor_matrix = TruthMatrixComposer().compose("a~b")
    polynomial = PolynomialComposer().compose(xor_matrix)
    post_summary = PostCriterionInspector().inspect(xor_matrix, polynomial)

    assert post_summary.keeps_zero is False
    assert post_summary.keeps_one is True
    assert post_summary.is_self_dual is False
    assert post_summary.is_monotone is False
    assert post_summary.is_linear is True

    _, redundant_matrix = TruthMatrixComposer().compose("a|!a")
    assert RedundantVariableInspector().inspect(redundant_matrix) == ("a",)


def test_main_creates_and_runs_cli(monkeypatch) -> None:
    """Проверяет запуск консольного интерфейса через main."""
    calls: list[str] = []

    class FakeCli:
        def run(self) -> None:
            calls.append("run")

    monkeypatch.setattr(main, "Lab2Cli", FakeCli)

    main.main()

    assert calls == ["run"]


def test_main_script_entrypoint(monkeypatch) -> None:
    """Проверяет блок запуска файла как скрипта."""
    calls: list[str] = []

    class FakeCli:
        def run(self) -> None:
            calls.append("run")

    monkeypatch.setattr("infrastructure.cli.Lab2Cli", FakeCli)

    runpy.run_path("LAB_2/src/main.py", run_name="__main__")

    assert calls == ["run"]


def test_main_module_is_reloadable() -> None:
    """Проверяет повторную загрузку точки входа."""
    importlib.reload(main)
