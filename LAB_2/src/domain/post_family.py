"""Проверка принадлежности функции классам Поста.

Свойства классов Поста важны для теоретического анализа функции.
Часть из них вычисляется напрямую по таблице истинности,
а линейность берется из уже построенного полинома Жегалкина.
"""

from domain.entities import PolynomialSummary, PostSummary, TruthMatrix


class PostCriterionInspector:
    """Проверяет булеву функцию на принадлежность классам Поста."""

    def inspect(
        self,
        truth_matrix: TruthMatrix,
        polynomial_summary: PolynomialSummary,
    ) -> PostSummary:
        """Собирает итоговую сводку по всем проверяемым свойствам."""
        return PostSummary(
            keeps_zero=self._check_zero_preservation(truth_matrix),
            keeps_one=self._check_one_preservation(truth_matrix),
            is_self_dual=self._check_self_duality(truth_matrix),
            is_monotone=self._check_monotonicity(truth_matrix),
            is_linear=polynomial_summary.is_linear,
        )

    def _check_zero_preservation(self, truth_matrix: TruthMatrix) -> bool:
        """Проверяет сохранение нуля: f(0,...,0) = 0."""
        if not truth_matrix.result_vector:
            return False
        return truth_matrix.result_vector[0] == 0

    def _check_one_preservation(self, truth_matrix: TruthMatrix) -> bool:
        """Проверяет сохранение единицы: f(1,...,1) = 1."""
        if not truth_matrix.result_vector:
            return False
        return truth_matrix.result_vector[-1] == 1

    def _check_self_duality(self, truth_matrix: TruthMatrix) -> bool:
        """Проверяет самодвойственность по дополнительным наборам."""
        result_vector = truth_matrix.result_vector
        if not result_vector:
            return False
        complement_mask = len(result_vector) - 1
        for index, value in enumerate(result_vector):
            if value == result_vector[complement_mask ^ index]:
                return False
        return True

    def _check_monotonicity(self, truth_matrix: TruthMatrix) -> bool:
        """Проверяет монотонность функции по частичному порядку наборов."""
        size = len(truth_matrix.result_vector)
        bit = 1
        while bit < size:
            for number in range(size):
                if number & bit:
                    continue
                if truth_matrix.result_vector[number] > truth_matrix.result_vector[number | bit]:
                    return False
            bit <<= 1
        return True
