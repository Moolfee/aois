"""Расчетно-табличный метод минимизации.

Этот метод сочетает два этапа:
1. сначала выполняет склеивание и получает простые импликанты;
2. затем строит таблицу покрытия, чтобы показать,
   как именно импликанты покрывают исходные строки.
"""

from domain.entities import CoverageTable, ReductionBundle, ReductionReport, TruthMatrix
from domain.minimization.base import ReductionSupport
from domain.settings import FORM_CONJUNCTION, FORM_DISJUNCTION, METHOD_TABLE


class TableCoverageEngine:
    """Минимизирует СДНФ и СКНФ с построением таблицы покрытия."""

    def __init__(self, support: ReductionSupport | None = None) -> None:
        """Сохраняет общий набор операций минимизации."""
        self._support = support or ReductionSupport()

    def minimize_pair(self, truth_matrix: TruthMatrix) -> ReductionBundle:
        """Выполняет расчетно-табличную минимизацию для обеих форм."""
        return ReductionBundle(
            disjunction_result=self._minimize_one(truth_matrix, FORM_DISJUNCTION),
            conjunction_result=self._minimize_one(truth_matrix, FORM_CONJUNCTION),
        )

    def _minimize_one(
        self,
        truth_matrix: TruthMatrix,
        target_form: str,
    ) -> ReductionReport:
        """Минимизирует одну форму и прикладывает таблицу покрытия."""
        source_numbers = self._support.pick_source_numbers(truth_matrix, target_form)
        if not source_numbers:
            return self._support.build_constant_report(METHOD_TABLE, target_form)
        prime_terms, merge_passes = self._support.generate_prime_patterns(
            source_numbers,
            len(truth_matrix.variable_names),
        )
        coverage_table = self._build_table(source_numbers, prime_terms)
        selected_terms = self._support.choose_cover(prime_terms, source_numbers)
        return self._support.make_report(
            strategy_name=METHOD_TABLE,
            target_form=target_form,
            source_numbers=source_numbers,
            merge_passes=merge_passes,
            variable_names=truth_matrix.variable_names,
            prime_terms=prime_terms,
            selected_terms=selected_terms,
            coverage_table=coverage_table,
        )

    def _build_table(
        self,
        source_numbers: tuple[int, ...],
        prime_terms: tuple[str, ...],
    ) -> CoverageTable:
        """Строит матрицу покрытия для найденных простых импликант."""
        return self._support.build_coverage_table(prime_terms, source_numbers)
