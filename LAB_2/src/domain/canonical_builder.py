"""Построение СДНФ и СКНФ по таблице истинности.

Логика здесь полностью следует определению канонических форм:
- СДНФ строится по наборам, где функция равна 1;
- СКНФ строится по наборам, где функция равна 0.
"""

from domain.entities import CanonicalForms, TruthMatrix


class CanonicalFormComposer:
    """Строит канонические формы по готовой таблице истинности."""

    def compose(self, truth_matrix: TruthMatrix) -> CanonicalForms:
        """Собирает текстовые формы и числовые наборы строк."""
        disjunction_numbers = tuple(
            row.number for row in truth_matrix.rows if row.result_value
        )
        conjunction_numbers = tuple(
            row.number for row in truth_matrix.rows if not row.result_value
        )
        disjunction_terms = [
            self._build_disjunction_term(truth_matrix.variable_names, row.values)
            for row in truth_matrix.rows
            if row.result_value
        ]
        conjunction_terms = [
            self._build_conjunction_term(truth_matrix.variable_names, row.values)
            for row in truth_matrix.rows
            if not row.result_value
        ]
        full_disjunction = "0"
        if disjunction_terms:
            full_disjunction = "|".join(disjunction_terms)
        full_conjunction = "1"
        if conjunction_terms:
            full_conjunction = "&".join(conjunction_terms)
        return CanonicalForms(
            full_disjunction=full_disjunction,
            full_conjunction=full_conjunction,
            disjunction_numbers=disjunction_numbers,
            conjunction_numbers=conjunction_numbers,
        )

    def _build_disjunction_term(
        self,
        variable_names: tuple[str, ...],
        values: dict[str, bool],
    ) -> str:
        """Строит один минтерм для СДНФ."""
        literal_list: list[str] = []
        for variable_name in variable_names:
            if values[variable_name]:
                literal_list.append(variable_name)
            else:
                literal_list.append(f"!{variable_name}")
        if len(literal_list) == 1:
            return literal_list[0]
        return f"({'&'.join(literal_list)})"

    def _build_conjunction_term(
        self,
        variable_names: tuple[str, ...],
        values: dict[str, bool],
    ) -> str:
        """Строит один макстерм для СКНФ."""
        literal_list: list[str] = []
        for variable_name in variable_names:
            if values[variable_name]:
                literal_list.append(f"!{variable_name}")
            else:
                literal_list.append(variable_name)
        if len(literal_list) == 1:
            return literal_list[0]
        return f"({'|'.join(literal_list)})"
