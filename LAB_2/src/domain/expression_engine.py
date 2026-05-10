"""Высокоуровневая работа с логическим выражением.

Здесь собраны операции, которые нужны практически всем этапам проекта:
1. построение дерева формулы;
2. сбор переменных из дерева;
3. вычисление значения формулы на одном конкретном наборе.
"""

from domain.entities import SyntaxNode
from domain.errors import EvaluationError, FormulaError
from domain.settings import (
    ALLOWED_NAMES,
    MAX_NAME_COUNT,
    SIGN_CONJUNCTION,
    SIGN_DISJUNCTION,
    SIGN_EQUIVALENCE,
    SIGN_IMPLICATION,
    SIGN_NEGATION,
)
from domain.syntax import FormulaTreeBuilder


class LogicExpressionEngine:
    """Разбирает и вычисляет логические выражения."""

    def __init__(self, tree_builder: FormulaTreeBuilder | None = None) -> None:
        """Сохраняет используемый синтаксический анализатор."""
        self._tree_builder = tree_builder or FormulaTreeBuilder()

    def build_tree(self, expression_text: str) -> SyntaxNode:
        """Преобразует текст формулы в синтаксическое дерево."""
        return self._tree_builder.build(expression_text)

    def collect_variables(self, syntax_tree: SyntaxNode) -> tuple[str, ...]:
        """Собирает все переменные, которые реально встречаются в формуле."""
        found_names: set[str] = set()
        self._collect_names(syntax_tree, found_names)
        if not found_names:
            raise FormulaError("В выражении не найдено переменных")
        invalid_names = tuple(
            sorted(name for name in found_names if name not in ALLOWED_NAMES)
        )
        if invalid_names:
            raise FormulaError(
                f"Недопустимые переменные: {', '.join(invalid_names)}"
            )
        if len(found_names) > MAX_NAME_COUNT:
            raise FormulaError("Поддерживается не более 5 переменных")
        return tuple(sorted(found_names))

    def evaluate(
        self,
        syntax_tree: SyntaxNode,
        variable_values: dict[str, bool],
    ) -> bool:
        """Вычисляет значение функции для одного набора переменных."""
        return self._evaluate_node(syntax_tree, variable_values)

    def _collect_names(self, node: SyntaxNode, found_names: set[str]) -> None:
        """Рекурсивно обходит дерево и извлекает все имена переменных."""
        if node.variable is not None:
            found_names.add(node.variable)
            return
        for child in node.children:
            self._collect_names(child, found_names)

    def _evaluate_node(
        self,
        node: SyntaxNode,
        variable_values: dict[str, bool],
    ) -> bool:
        """Рекурсивно вычисляет значение поддерева.

        Для листа дерева просто берется значение переменной,
        а для внутреннего узла применяется соответствующая логическая операция.
        """
        if node.variable is not None:
            if node.variable not in variable_values:
                raise EvaluationError(
                    f"Не задано значение переменной: {node.variable}"
                )
            return variable_values[node.variable]

        # Отрицание использует только одного ребенка.
        if node.operation == SIGN_NEGATION:
            return not self._evaluate_node(node.children[0], variable_values)

        # Все остальные операции в проекте бинарные,
        # поэтому сначала вычисляем оба аргумента.
        left_value = self._evaluate_node(node.children[0], variable_values)
        right_value = self._evaluate_node(node.children[1], variable_values)

        if node.operation == SIGN_CONJUNCTION:
            return left_value and right_value
        if node.operation == SIGN_DISJUNCTION:
            return left_value or right_value
        if node.operation == SIGN_IMPLICATION:
            return (not left_value) or right_value
        if node.operation == SIGN_EQUIVALENCE:
            return left_value == right_value
        raise EvaluationError(f"Неизвестная операция: {node.operation}")
