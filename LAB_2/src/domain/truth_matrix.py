"""Построение таблицы истинности.

Это один из ключевых модулей всей лабораторной.
Почти все дальнейшие результаты вычисляются именно из таблицы истинности,
поэтому важно, что она строится в строгом и стабильном порядке наборов.
"""

from domain.entities import SyntaxNode, TruthMatrix, TruthRow
from domain.expression_engine import LogicExpressionEngine


class TruthMatrixComposer:
    """Строит таблицу истинности для заданной логической функции."""

    def __init__(self, expression_engine: LogicExpressionEngine | None = None) -> None:
        """Сохраняет движок, который умеет разбирать и вычислять формулу."""
        self._expression_engine = expression_engine or LogicExpressionEngine()

    def compose(self, expression_text: str) -> tuple[SyntaxNode, TruthMatrix]:
        """Разбирает выражение и строит для него полную таблицу истинности."""
        syntax_tree = self._expression_engine.build_tree(expression_text)
        variable_names = self._expression_engine.collect_variables(syntax_tree)
        rows = self._build_rows(syntax_tree, variable_names)
        result_vector = tuple(int(row.result_value) for row in rows)
        return syntax_tree, TruthMatrix(
            variable_names=variable_names,
            rows=rows,
            result_vector=result_vector,
        )

    def _build_rows(
        self,
        syntax_tree: SyntaxNode,
        variable_names: tuple[str, ...],
    ) -> tuple[TruthRow, ...]:
        """Строит все строки таблицы в двоичном порядке номеров наборов."""
        row_list: list[TruthRow] = []
        table_size = 1 << len(variable_names)
        for number in range(table_size):
            assignment = self._build_assignment(variable_names, number)
            result_value = self._expression_engine.evaluate(syntax_tree, assignment)
            row_list.append(
                TruthRow(
                    number=number,
                    values=assignment,
                    result_value=result_value,
                )
            )
        return tuple(row_list)

    def _build_assignment(
        self,
        variable_names: tuple[str, ...],
        number: int,
    ) -> dict[str, bool]:
        """Преобразует номер строки в отображение переменных в значения."""
        assignment: dict[str, bool] = {}
        variable_count = len(variable_names)
        for position, variable_name in enumerate(variable_names):
            bit = 1 << (variable_count - position - 1)
            assignment[variable_name] = bool(number & bit)
        return assignment
