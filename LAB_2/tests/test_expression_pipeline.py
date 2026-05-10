"""Тесты полного пути обработки выражения.

Здесь проверяются базовые кирпичики проекта:
разбор, вычисление, таблица истинности и канонические формы.
"""

import pytest

from domain.canonical_builder import CanonicalFormComposer
from domain.errors import FormulaError
from domain.expression_engine import LogicExpressionEngine
from domain.index_presenter import IndexEncoder
from domain.truth_matrix import TruthMatrixComposer


def test_expression_pipeline_supports_unicode_symbols() -> None:
    """Проверяет, что парсер понимает Unicode-обозначения логики."""
    engine = LogicExpressionEngine()
    syntax_tree = engine.build_tree("!(!a→!b)∨c")
    variables = engine.collect_variables(syntax_tree)

    assert variables == ("a", "b", "c")
    assert engine.evaluate(
        syntax_tree,
        {"a": False, "b": True, "c": False},
    ) is True


def test_truth_matrix_and_forms_for_and() -> None:
    """Проверяет таблицу истинности, СДНФ, СКНФ и индекс для `a&b`."""
    _, truth_matrix = TruthMatrixComposer().compose("a&b")
    assert truth_matrix.variable_names == ("a", "b")
    assert truth_matrix.result_vector == (0, 0, 0, 1)

    canonical_forms = CanonicalFormComposer().compose(truth_matrix)
    assert canonical_forms.full_disjunction == "(a&b)"
    assert canonical_forms.full_conjunction == "(a|b)&(a|!b)&(!a|b)"
    assert canonical_forms.disjunction_numbers == (3,)
    assert canonical_forms.conjunction_numbers == (0, 1, 2)

    index_presentation = IndexEncoder().encode(truth_matrix)
    assert index_presentation.bit_vector == "0001"
    assert index_presentation.decimal_value == 1


def test_expression_pipeline_raises_on_invalid_input() -> None:
    """Проверяет, что недопустимые символы не проходят токенизацию."""
    engine = LogicExpressionEngine()
    with pytest.raises(FormulaError):
        engine.build_tree("a+b")
