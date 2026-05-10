"""Построение полинома Жегалкина.

Полином Жегалкина — это алгебраическая нормальная форма булевой функции.
В проекте коэффициенты полинома вычисляются через треугольник XOR-разностей.
"""

from domain.entities import PolynomialSummary, TruthMatrix


class PolynomialComposer:
    """Строит полином Жегалкина для булевой функции."""

    def compose(self, truth_matrix: TruthMatrix) -> PolynomialSummary:
        """Собирает коэффициенты, мономы, текст формулы и признак линейности."""
        triangle = self._build_triangle(truth_matrix)
        coefficients = tuple(row[0] for row in triangle if row)
        monomials = self._build_monomials(coefficients, truth_matrix.variable_names)
        formula_text = self._build_formula_text(monomials)
        is_linear = self._check_linearity(monomials)
        return PolynomialSummary(
            coefficients=coefficients,
            monomials=monomials,
            formula_text=formula_text,
            is_linear=is_linear,
        )

    def _build_triangle(self, truth_matrix: TruthMatrix) -> tuple[tuple[int, ...], ...]:
        """Строит треугольник конечных XOR-разностей."""
        triangle_rows: list[tuple[int, ...]] = [truth_matrix.result_vector]
        while len(triangle_rows[-1]) > 1:
            previous_row = triangle_rows[-1]
            next_row = []
            for index in range(len(previous_row) - 1):
                next_row.append(previous_row[index] ^ previous_row[index + 1])
            triangle_rows.append(tuple(next_row))
        return tuple(triangle_rows)

    def _build_monomials(
        self,
        coefficients: tuple[int, ...],
        variable_names: tuple[str, ...],
    ) -> tuple[tuple[str, ...], ...]:
        """Преобразует ненулевые коэффициенты в наборы переменных монома."""
        monomial_list: list[tuple[str, ...]] = []
        variable_count = len(variable_names)
        for mask, coefficient in enumerate(coefficients):
            if coefficient == 0:
                continue
            current_monomial: list[str] = []
            for position, variable_name in enumerate(variable_names):
                bit = 1 << (variable_count - position - 1)
                if mask & bit:
                    current_monomial.append(variable_name)
            monomial_list.append(tuple(current_monomial))
        return tuple(monomial_list)

    def _build_formula_text(
        self,
        monomials: tuple[tuple[str, ...], ...],
    ) -> str:
        """Собирает человекочитаемую запись полинома."""
        if not monomials:
            return "0"
        part_list: list[str] = []
        for monomial in monomials:
            if not monomial:
                part_list.append("1")
            else:
                part_list.append("*".join(monomial))
        return " ^ ".join(part_list)

    def _check_linearity(self, monomials: tuple[tuple[str, ...], ...]) -> bool:
        """Определяет линейность по степеням мономов."""
        for monomial in monomials:
            if len(monomial) > 1:
                return False
        return True
