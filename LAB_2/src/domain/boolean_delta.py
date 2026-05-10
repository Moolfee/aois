"""Булевы производные функции.

Этот модуль отвечает за частные и смешанные производные.
С логической точки зрения производная показывает,
меняется ли функция при изменении выбранной переменной.
"""

from itertools import combinations

from domain.canonical_builder import CanonicalFormComposer
from domain.entities import CanonicalForms, DerivativeSummary, TruthMatrix, TruthRow
from domain.settings import MAX_DERIVATIVE_DEPTH


class DerivativeWorkshop:
    """Строит частные и смешанные булевы производные."""

    def __init__(
        self,
        canonical_form_composer: CanonicalFormComposer | None = None,
    ) -> None:
        """Сохраняет построитель канонических форм для производных."""
        self._canonical_form_composer = (
            canonical_form_composer or CanonicalFormComposer()
        )

    def build_all(
        self,
        truth_matrix: TruthMatrix,
        max_depth: int = MAX_DERIVATIVE_DEPTH,
    ) -> dict[tuple[str, ...], DerivativeSummary]:
        """Строит производные по всем комбинациям переменных допустимой длины."""
        derivative_map: dict[tuple[str, ...], DerivativeSummary] = {}
        effective_depth = min(max_depth, len(truth_matrix.variable_names))
        for group_size in range(1, effective_depth + 1):
            for variable_group in combinations(truth_matrix.variable_names, group_size):
                derivative_map[variable_group] = self.build_for_group(
                    truth_matrix,
                    variable_group,
                )
        return derivative_map

    def build_for_group(
        self,
        truth_matrix: TruthMatrix,
        variable_group: tuple[str, ...],
    ) -> DerivativeSummary:
        """Строит одну производную по конкретной группе переменных."""
        derivative_table = self._build_derivative_table(truth_matrix, variable_group)
        derivative_forms = self._pack_forms(derivative_table)
        changed_rows = tuple(
            index
            for index, value in enumerate(derivative_table.result_vector)
            if value == 1
        )
        return DerivativeSummary(
            variable_group=variable_group,
            result_vector=derivative_table.result_vector,
            changed_rows=changed_rows,
            full_disjunction=derivative_forms.full_disjunction,
            full_conjunction=derivative_forms.full_conjunction,
        )

    def _build_derivative_table(
        self,
        truth_matrix: TruthMatrix,
        variable_group: tuple[str, ...],
    ) -> TruthMatrix:
        """Строит таблицу истинности уже для производной функции."""
        current_vector = list(truth_matrix.result_vector)
        for variable_name in variable_group:
            # XOR с набором, у которого перевернут один нужный бит,
            # реализует стандартное определение булевой производной.
            bit = self._variable_bit(truth_matrix.variable_names, variable_name)
            next_vector: list[int] = []
            for number in range(len(current_vector)):
                next_vector.append(current_vector[number] ^ current_vector[number ^ bit])
            current_vector = next_vector

        row_list: list[TruthRow] = []
        for row, value in zip(truth_matrix.rows, current_vector, strict=True):
            row_list.append(
                TruthRow(
                    number=row.number,
                    values=dict(row.values),
                    result_value=bool(value),
                )
            )
        return TruthMatrix(
            variable_names=truth_matrix.variable_names,
            rows=tuple(row_list),
            result_vector=tuple(current_vector),
        )

    def _pack_forms(self, derivative_table: TruthMatrix) -> CanonicalForms:
        """Строит СДНФ и СКНФ для найденной производной."""
        return self._canonical_form_composer.compose(derivative_table)

    def _variable_bit(
        self,
        variable_names: tuple[str, ...],
        variable_name: str,
    ) -> int:
        """Находит бит, соответствующий выбранной переменной."""
        variable_count = len(variable_names)
        position = variable_names.index(variable_name)
        return 1 << (variable_count - position - 1)
