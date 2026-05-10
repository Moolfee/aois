"""Тесты прикладного сервиса и форматтера."""

from application.lab2_service import Lab2Service
from infrastructure.report_printer import StudyReportPrinter


def test_service_builds_full_report() -> None:
    """Проверяет, что сервис действительно собирает все разделы анализа."""
    study_result = Lab2Service().study_function("a&b")

    assert study_result.truth_matrix.variable_names == ("a", "b")
    assert study_result.canonical_forms.full_disjunction == "(a&b)"
    assert study_result.index_presentation.bit_vector == "0001"
    assert study_result.polynomial_summary.formula_text == "a*b"
    assert study_result.redundant_variables == tuple()
    assert ("a", "b") in study_result.derivatives
    assert study_result.glue_reduction.disjunction_result.minimized_formula == "(a&b)"
    assert study_result.table_reduction.conjunction_result.coverage_table is not None
    assert study_result.map_reduction.disjunction_result.map_layers


def test_report_printer_contains_all_main_sections() -> None:
    """Проверяет, что текстовый отчет содержит все ключевые блоки в новом виде."""
    study_result = Lab2Service().study_function("a&b")
    text = StudyReportPrinter().format(study_result)

    assert "=== 1. ИСХОДНАЯ ФУНКЦИЯ ===" in text
    assert "=== 2. ТАБЛИЦА ИСТИННОСТИ ===" in text
    assert "=== 3. СОВЕРШЕННЫЕ ФОРМЫ ===" in text
    assert "=== 6. КЛАССЫ ПОСТА ===" in text
    assert "=== 7. ПОЛИНОМ ЖЕГАЛКИНА ===" in text
    assert "=== 9. БУЛЕВЫ ПРОИЗВОДНЫЕ ===" in text
    assert "=== 12. ТАБЛИЧНЫЙ МЕТОД (КАРТА КАРНО) ===" in text
