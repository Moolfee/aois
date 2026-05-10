"""Поиск фиктивных переменных.

Переменная считается фиктивной, если при ее переключении
значение функции нигде не меняется.
"""

from domain.entities import TruthMatrix


class RedundantVariableInspector:
    """Находит переменные, не влияющие на значение функции."""

    def inspect(self, truth_matrix: TruthMatrix) -> tuple[str, ...]:
        """Перебирает все переменные и оставляет только фиктивные."""
        redundant_names: list[str] = []
        for variable_name in truth_matrix.variable_names:
            if not self._value_changes(truth_matrix, variable_name):
                redundant_names.append(variable_name)
        return tuple(redundant_names)

    def _value_changes(self, truth_matrix: TruthMatrix, variable_name: str) -> bool:
        """Проверяет, существует ли хотя бы один набор, где переменная влияет."""
        bit = self._variable_bit(truth_matrix.variable_names, variable_name)
        for number in range(len(truth_matrix.result_vector)):
            if truth_matrix.result_vector[number] != truth_matrix.result_vector[number ^ bit]:
                return True
        return False

    def _variable_bit(
        self,
        variable_names: tuple[str, ...],
        variable_name: str,
    ) -> int:
        """Вычисляет бит позиции переменной в двоичном номере набора."""
        variable_count = len(variable_names)
        position = variable_names.index(variable_name)
        return 1 << (variable_count - position - 1)
