"""Построение индексной формы.

Индексная форма — это вектор значений функции и число,
которое получается при интерпретации этого вектора как двоичного кода.
"""

from domain.entities import IndexPresentation, TruthMatrix


class IndexEncoder:
    """Строит индексную форму функции."""

    def encode(self, truth_matrix: TruthMatrix) -> IndexPresentation:
        """Преобразует вектор значений в строковое и числовое представление."""
        bit_vector = "".join(str(value) for value in truth_matrix.result_vector)
        decimal_value = 0
        if bit_vector:
            decimal_value = int(bit_vector, 2)
        return IndexPresentation(bit_vector=bit_vector, decimal_value=decimal_value)
