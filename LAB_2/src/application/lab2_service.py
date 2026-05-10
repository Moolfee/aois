"""Фасад прикладного слоя для полной обработки логической функции.

Именно этот модуль связывает между собой все этапы лабораторной:
разбор выражения, построение таблицы истинности, канонических форм,
полинома Жегалкина, проверок по Посту, производных и минимизации.
"""

from dataclasses import dataclass

from domain.boolean_delta import DerivativeWorkshop
from domain.canonical_builder import CanonicalFormComposer
from domain.entities import FunctionStudyResult, ReductionBundle
from domain.expression_engine import LogicExpressionEngine
from domain.index_presenter import IndexEncoder
from domain.post_family import PostCriterionInspector
from domain.redundant_variable_finder import RedundantVariableInspector
from domain.truth_matrix import TruthMatrixComposer
from domain.zhegalkin_transform import PolynomialComposer
from domain.minimization.coverage_reduce import TableCoverageEngine
from domain.minimization.kmap_reduce import KarnaughMapEngine
from domain.minimization.merge_reduce import GlueReductionEngine


@dataclass(frozen=True)
class ServiceParts:
    """Контейнер зависимостей сервиса.

    Такой объект полезен по двум причинам:
    1. код `Lab2Service` остается чище;
    2. зависимости можно легко подменять в тестах.
    """

    expression_engine: LogicExpressionEngine
    truth_matrix_composer: TruthMatrixComposer
    canonical_form_composer: CanonicalFormComposer
    index_encoder: IndexEncoder
    polynomial_composer: PolynomialComposer
    post_criterion_inspector: PostCriterionInspector
    redundant_variable_inspector: RedundantVariableInspector
    derivative_workshop: DerivativeWorkshop
    glue_reduction_engine: GlueReductionEngine
    table_coverage_engine: TableCoverageEngine
    karnaugh_map_engine: KarnaughMapEngine


class Lab2Service:
    """Координирует полный анализ булевой функции."""

    def __init__(
        self,
        parts: ServiceParts | None = None,
    ) -> None:
        """Собирает стандартный набор доменных сервисов.

        Если зависимости не переданы снаружи, создаются рабочие объекты
        по умолчанию. Это основной путь для обычного запуска программы.
        """
        if parts is None:
            expression_engine = LogicExpressionEngine()
            truth_matrix_composer = TruthMatrixComposer(expression_engine)
            canonical_form_composer = CanonicalFormComposer()
            reduction_support = None
            parts = ServiceParts(
                expression_engine=expression_engine,
                truth_matrix_composer=truth_matrix_composer,
                canonical_form_composer=canonical_form_composer,
                index_encoder=IndexEncoder(),
                polynomial_composer=PolynomialComposer(),
                post_criterion_inspector=PostCriterionInspector(),
                redundant_variable_inspector=RedundantVariableInspector(),
                derivative_workshop=DerivativeWorkshop(canonical_form_composer),
                glue_reduction_engine=GlueReductionEngine(reduction_support),
                table_coverage_engine=TableCoverageEngine(reduction_support),
                karnaugh_map_engine=KarnaughMapEngine(reduction_support),
            )
        self._parts = parts

    def study_function(self, expression_text: str) -> FunctionStudyResult:
        """Выполняет все этапы анализа для одной функции.

        Здесь особенно важно то, что все вычисления идут от одной и той же
        таблицы истинности. Это делает результат согласованным:
        СДНФ, СКНФ, индекс, производные и минимизация опираются
        на один и тот же базовый набор значений функции.
        """
        syntax_tree, truth_matrix = self._parts.truth_matrix_composer.compose(
            expression_text
        )
        # Канонические формы строятся именно по таблице истинности,
        # а не по исходной строке напрямую.
        canonical_forms = self._parts.canonical_form_composer.compose(truth_matrix)
        index_presentation = self._parts.index_encoder.encode(truth_matrix)
        polynomial_summary = self._parts.polynomial_composer.compose(truth_matrix)
        post_summary = self._parts.post_criterion_inspector.inspect(
            truth_matrix,
            polynomial_summary,
        )
        redundant_variables = self._parts.redundant_variable_inspector.inspect(
            truth_matrix
        )
        derivatives = self._parts.derivative_workshop.build_all(truth_matrix)
        glue_reduction = self._parts.glue_reduction_engine.minimize_pair(truth_matrix)
        table_reduction = self._parts.table_coverage_engine.minimize_pair(truth_matrix)
        map_reduction = self._parts.karnaugh_map_engine.minimize_pair(truth_matrix)
        return FunctionStudyResult(
            expression_text=expression_text,
            syntax_tree=syntax_tree,
            truth_matrix=truth_matrix,
            canonical_forms=canonical_forms,
            index_presentation=index_presentation,
            polynomial_summary=polynomial_summary,
            post_summary=post_summary,
            redundant_variables=redundant_variables,
            derivatives=derivatives,
            glue_reduction=glue_reduction,
            table_reduction=table_reduction,
            map_reduction=map_reduction,
        )

    def minimize_all(
        self,
        study_result: FunctionStudyResult,
    ) -> tuple[ReductionBundle, ReductionBundle, ReductionBundle]:
        """Повторно запускает только блок минимизации.

        Метод полезен как дополнительная точка входа: если полный отчет уже
        построен, можно отдельно запросить только результаты минимизации.
        """
        truth_matrix = study_result.truth_matrix
        return (
            self._parts.glue_reduction_engine.minimize_pair(truth_matrix),
            self._parts.table_coverage_engine.minimize_pair(truth_matrix),
            self._parts.karnaugh_map_engine.minimize_pair(truth_matrix),
        )
