"""Расчетный метод минимизации.

В этом варианте мы последовательно склеиваем термы
и формируем простые импликанты без построения таблицы покрытия на бумаге.
"""

from domain.entities import ReductionBundle, ReductionReport, TruthMatrix
from domain.minimization.base import ReductionSupport
from domain.settings import FORM_CONJUNCTION, FORM_DISJUNCTION, METHOD_GLUE


class GlueReductionEngine:
    """Минимизирует СДНФ и СКНФ за счет последовательного склеивания."""

    def __init__(self, support: ReductionSupport | None = None) -> None:
        """Сохраняет общий набор вспомогательных операций."""
        self._support = support or ReductionSupport()

    def minimize_pair(self, truth_matrix: TruthMatrix) -> ReductionBundle:
        """Запускает расчетную минимизацию сразу для обеих форм."""
        return ReductionBundle(
            disjunction_result=self._minimize_one(truth_matrix, FORM_DISJUNCTION),
            conjunction_result=self._minimize_one(truth_matrix, FORM_CONJUNCTION),
        )

    def _minimize_one(
        self,
        truth_matrix: TruthMatrix,
        target_form: str,
    ) -> ReductionReport:
        """Минимизирует только одну выбранную форму."""
        source_numbers = self._support.pick_source_numbers(truth_matrix, target_form)
        if not source_numbers:
            return self._support.build_constant_report(METHOD_GLUE, target_form)
        prime_terms, merge_passes = self._support.generate_prime_patterns(
            source_numbers,
            len(truth_matrix.variable_names),
        )
        selected_terms = self._support.choose_cover(prime_terms, source_numbers)
        return self._support.make_report(
            strategy_name=METHOD_GLUE,
            target_form=target_form,
            source_numbers=source_numbers,
            merge_passes=merge_passes,
            variable_names=truth_matrix.variable_names,
            prime_terms=prime_terms,
            selected_terms=selected_terms,
        )
