"""Тесты полного пути обработки выражения.

Здесь проверяются базовые кирпичики проекта:
разбор, вычисление, таблица истинности и канонические формы.
"""

import pytest

from domain.canonical_builder import CanonicalFormComposer
from domain.entities import SyntaxNode
from domain.errors import EvaluationError, FormulaError
from domain.expression_engine import LogicExpressionEngine
from domain.index_presenter import IndexEncoder
from domain.lexical import FormulaScanner
from domain.settings import SIGN_EQUIVALENCE
from domain.syntax import FormulaTreeBuilder
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


def test_scanner_accepts_aliases_gaps_and_rejects_empty_text() -> None:
    """Проверяет нормализацию символов и пустого ввода."""
    tokens = FormulaScanner().scan(" \n A ⇒ b ↔ ¬c ")

    assert [token.text for token in tokens] == ["a", "->", "b", "~", "!", "c"]

    with pytest.raises(FormulaError):
        FormulaScanner().scan("   ")


def test_parser_reports_common_syntax_errors() -> None:
    """Проверяет основные ошибки рекурсивного спуска."""
    builder = FormulaTreeBuilder()

    with pytest.raises(FormulaError, match="закрывающая"):
        builder.build("(a&b")

    with pytest.raises(FormulaError, match="Лишние"):
        builder.build("a b")

    with pytest.raises(FormulaError, match="Ожидался операнд"):
        builder.build("a&")

    with pytest.raises(FormulaError, match="Ожидался операнд"):
        builder.build("&a")


def test_engine_reports_variable_and_operation_errors() -> None:
    """Проверяет ошибки сбора переменных и вычисления дерева."""
    engine = LogicExpressionEngine()

    with pytest.raises(FormulaError, match="не найдено"):
        engine.collect_variables(SyntaxNode(operation=None, variable=None, children=tuple()))

    syntax_tree = engine.build_tree("a")
    with pytest.raises(EvaluationError, match="Не задано"):
        engine.evaluate(syntax_tree, {})

    unknown_operation = SyntaxNode(
        operation="?",
        variable=None,
        children=(
            SyntaxNode(operation=None, variable="a", children=tuple()),
            SyntaxNode(operation=None, variable="b", children=tuple()),
        ),
    )
    with pytest.raises(EvaluationError, match="Неизвестная операция"):
        engine.evaluate(unknown_operation, {"a": True, "b": False})


def test_equivalence_is_evaluated() -> None:
    """Проверяет ветку вычисления эквивалентности."""
    engine = LogicExpressionEngine()
    syntax_tree = engine.build_tree("a~b")

    assert syntax_tree.operation == SIGN_EQUIVALENCE
    assert engine.evaluate(syntax_tree, {"a": True, "b": True}) is True
    assert engine.evaluate(syntax_tree, {"a": True, "b": False}) is False
