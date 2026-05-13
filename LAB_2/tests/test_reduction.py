"""Тесты минимизации.

Набор проверяет, что все три метода действительно дают
корректный и ожидаемый результат на простых функциях.
"""

from domain.minimization.coverage_reduce import TableCoverageEngine
from domain.minimization.kmap_reduce import KarnaughMapEngine
from domain.minimization.base import PatternRecord, ReductionSupport
from domain.minimization.merge_reduce import GlueReductionEngine
from domain.settings import FORM_CONJUNCTION, FORM_DISJUNCTION
from domain.truth_matrix import TruthMatrixComposer


def test_reduction_engines_for_and_function() -> None:
    """Сверяет три метода минимизации на функции `a&b`."""
    _, truth_matrix = TruthMatrixComposer().compose("a&b")

    glue_result = GlueReductionEngine().minimize_pair(truth_matrix)
    assert glue_result.disjunction_result.minimized_formula == "(a&b)"
    assert set(glue_result.conjunction_result.selected_terms) == {"0-", "-0"}

    table_result = TableCoverageEngine().minimize_pair(truth_matrix)
    assert table_result.conjunction_result.coverage_table is not None
    assert table_result.conjunction_result.coverage_table.column_numbers == (0, 1, 2)

    map_result = KarnaughMapEngine().minimize_pair(truth_matrix)
    assert map_result.disjunction_result.minimized_formula == "(a&b)"
    assert map_result.disjunction_result.map_layers


def test_reduction_constant_zero_case() -> None:
    """Проверяет вырожденный случай функции, тождественно равной нулю."""
    _, truth_matrix = TruthMatrixComposer().compose("a&!a")
    result = GlueReductionEngine().minimize_pair(truth_matrix)
    assert result.disjunction_result.minimized_formula == "0"


def test_support_formats_patterns_and_constants() -> None:
    """Покрывает перевод шаблонов в формулы для обеих форм."""
    support = ReductionSupport()

    assert support.build_empty_bundle("method").disjunction_result.minimized_formula == "0"
    assert support.pattern_to_formula("--", ("a", "b"), FORM_DISJUNCTION) == "1"
    assert support.pattern_to_formula("--", ("a", "b"), FORM_CONJUNCTION) == "0"
    assert support.pattern_to_formula("1-", ("a", "b"), FORM_DISJUNCTION) == "a"
    assert support.pattern_to_formula("0-", ("a", "b"), FORM_CONJUNCTION) == "a"
    assert support.pattern_to_formula("10", ("a", "b"), FORM_CONJUNCTION) == "(!a|b)"
    assert support.join_formula_terms(("a", "b"), FORM_CONJUNCTION) == "a&b"


def test_support_merge_and_cover_edge_cases() -> None:
    """Проверяет труднодоступные ветки склеивания и выбора покрытия."""
    support = ReductionSupport()

    left = PatternRecord("0-", frozenset({0, 1}))
    right = PatternRecord("-1", frozenset({1, 3}))
    assert support._merge_two_records(left, right) is None
    assert support._merge_two_records(
        PatternRecord("00", frozenset({0})),
        PatternRecord("11", frozenset({3})),
    ) is None

    selected = support.choose_cover(("0-", "-1", "1-"), (0, 1, 2))
    assert selected == ("0-", "1-")

    assert support.choose_cover(("00",), (0, 1)) == ("00",)


def test_reduction_engines_handle_constant_one_and_five_variables() -> None:
    """Проверяет константу единицы и два слоя карты Карно."""
    _, constant_one = TruthMatrixComposer().compose("a|!a")
    glue_result = GlueReductionEngine().minimize_pair(constant_one)
    table_result = TableCoverageEngine().minimize_pair(constant_one)

    assert glue_result.conjunction_result.minimized_formula == "1"
    assert table_result.disjunction_result.coverage_table is not None

    _, five_variable_matrix = TruthMatrixComposer().compose("a&b&c&d&e")
    map_result = KarnaughMapEngine().minimize_pair(five_variable_matrix)

    assert [layer.title for layer in map_result.disjunction_result.map_layers] == [
        "e=0",
        "e=1",
    ]
    assert map_result.disjunction_result.minimized_formula == "(a&b&c&d&e)"
