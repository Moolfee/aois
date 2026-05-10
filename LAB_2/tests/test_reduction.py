"""Тесты минимизации.

Набор проверяет, что все три метода действительно дают
корректный и ожидаемый результат на простых функциях.
"""

from domain.minimization.coverage_reduce import TableCoverageEngine
from domain.minimization.kmap_reduce import KarnaughMapEngine
from domain.minimization.merge_reduce import GlueReductionEngine
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
