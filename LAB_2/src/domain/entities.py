"""Структуры данных, которыми обмениваются модули проекта.

Все dataclass в этом файле — это не алгоритмы, а контейнеры результата.
Они задают единый формат представления токенов, узлов дерева,
таблицы истинности, полинома, производных и минимизации.
"""

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenUnit:
    """Один токен логической формулы.

    `kind` — тип токена.
    `text` — исходный текст токена после нормализации.
    `start_at` — позиция токена в строке.
    """

    kind: str
    text: str
    start_at: int


@dataclass(frozen=True)
class SyntaxNode:
    """Один узел синтаксического дерева выражения."""

    operation: str | None
    variable: str | None
    children: tuple["SyntaxNode", ...]


@dataclass(frozen=True)
class TruthRow:
    """Одна строка таблицы истинности."""

    number: int
    values: dict[str, bool]
    result_value: bool


@dataclass(frozen=True)
class TruthMatrix:
    """Полная таблица истинности функции."""

    variable_names: tuple[str, ...]
    rows: tuple[TruthRow, ...]
    result_vector: tuple[int, ...]


@dataclass(frozen=True)
class CanonicalForms:
    """СДНФ, СКНФ и их числовые представления."""

    full_disjunction: str
    full_conjunction: str
    disjunction_numbers: tuple[int, ...]
    conjunction_numbers: tuple[int, ...]


@dataclass(frozen=True)
class IndexPresentation:
    """Индексная форма функции: вектор и его десятичный индекс."""

    bit_vector: str
    decimal_value: int


@dataclass(frozen=True)
class PostSummary:
    """Результат проверки принадлежности классам Поста."""

    keeps_zero: bool
    keeps_one: bool
    is_self_dual: bool
    is_monotone: bool
    is_linear: bool


@dataclass(frozen=True)
class PolynomialSummary:
    """Представление функции в виде полинома Жегалкина."""

    coefficients: tuple[int, ...]
    monomials: tuple[tuple[str, ...], ...]
    formula_text: str
    is_linear: bool


@dataclass(frozen=True)
class DerivativeSummary:
    """Описание одной булевой производной."""

    variable_group: tuple[str, ...]
    result_vector: tuple[int, ...]
    changed_rows: tuple[int, ...]
    full_disjunction: str
    full_conjunction: str


@dataclass(frozen=True)
class MergePair:
    """Два терма, которые удалось склеить."""

    left_term: str
    right_term: str
    merged_term: str


@dataclass(frozen=True)
class MergePass:
    """Один проход алгоритма склеивания."""

    pass_number: int
    source_terms: tuple[str, ...]
    merged_pairs: tuple[MergePair, ...]
    produced_terms: tuple[str, ...]
    leftover_terms: tuple[str, ...]


@dataclass(frozen=True)
class CoverageTable:
    """Таблица покрытия для расчетно-табличного метода."""

    column_numbers: tuple[int, ...]
    row_terms: tuple[str, ...]
    marks: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class MapLayer:
    """Один слой карты Карно."""

    title: str
    row_labels: tuple[str, ...]
    column_labels: tuple[str, ...]
    cells: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class ReductionReport:
    """Результат одной стратегии минимизации для одной формы."""

    strategy_name: str
    target_form: str
    source_numbers: tuple[int, ...]
    prime_terms: tuple[str, ...]
    selected_terms: tuple[str, ...]
    minimized_formula: str
    merge_passes: tuple[MergePass, ...]
    coverage_table: CoverageTable | None
    map_layers: tuple[MapLayer, ...]


@dataclass(frozen=True)
class ReductionBundle:
    """Пара результатов минимизации: для СДНФ и для СКНФ."""

    disjunction_result: ReductionReport
    conjunction_result: ReductionReport


@dataclass(frozen=True)
class FunctionStudyResult:
    """Итоговая сводка по всем этапам анализа функции."""

    expression_text: str
    syntax_tree: SyntaxNode
    truth_matrix: TruthMatrix
    canonical_forms: CanonicalForms
    index_presentation: IndexPresentation
    polynomial_summary: PolynomialSummary
    post_summary: PostSummary
    redundant_variables: tuple[str, ...]
    derivatives: dict[tuple[str, ...], DerivativeSummary]
    glue_reduction: ReductionBundle
    table_reduction: ReductionBundle
    map_reduction: ReductionBundle


sys.modules.setdefault("src.domain.entities", sys.modules[__name__])
