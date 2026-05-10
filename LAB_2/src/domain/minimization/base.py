"""Общие инструменты для всех методов минимизации.

Именно этот файл содержит базовые операции над импликантами:
1. перевод номера строки в двоичный шаблон;
2. проверку покрытия строки шаблоном;
3. склеивание совместимых термов;
4. построение таблицы покрытия;
5. выбор набора импликант, покрывающих исходные строки.
"""

from dataclasses import dataclass

from domain.entities import (
    CoverageTable,
    MapLayer,
    MergePair,
    MergePass,
    ReductionBundle,
    ReductionReport,
    TruthMatrix,
)
from domain.settings import (
    FORM_CONJUNCTION,
    FORM_DISJUNCTION,
)


@dataclass(frozen=True)
class PatternRecord:
    """Один шаблон импликанты и множество покрываемых строк."""

    pattern: str
    covered_numbers: frozenset[int]


class ReductionSupport:
    """Набор переиспользуемых операций для минимизации."""

    def build_empty_bundle(self, strategy_name: str) -> ReductionBundle:
        """Строит пустой результат для обеих форм сразу."""
        return ReductionBundle(
            disjunction_result=self.build_constant_report(
                strategy_name,
                FORM_DISJUNCTION,
            ),
            conjunction_result=self.build_constant_report(
                strategy_name,
                FORM_CONJUNCTION,
            ),
        )

    def pick_source_numbers(
        self,
        truth_matrix: TruthMatrix,
        target_form: str,
    ) -> tuple[int, ...]:
        """Выбирает номера строк, которые нужно покрыть при минимизации.

        Для СДНФ это строки со значением 1.
        Для СКНФ это строки со значением 0.
        """
        target_value = 1
        if target_form == FORM_CONJUNCTION:
            target_value = 0
        return tuple(
            index
            for index, value in enumerate(truth_matrix.result_vector)
            if value == target_value
        )

    def build_constant_report(
        self,
        strategy_name: str,
        target_form: str,
        map_layers: tuple[MapLayer, ...] = tuple(),
        coverage_table: CoverageTable | None = None,
    ) -> ReductionReport:
        """Строит отчет для вырожденного случая константной функции."""
        return ReductionReport(
            strategy_name=strategy_name,
            target_form=target_form,
            source_numbers=tuple(),
            prime_terms=tuple(),
            selected_terms=tuple(),
            minimized_formula=self.constant_formula(target_form),
            merge_passes=tuple(),
            coverage_table=coverage_table,
            map_layers=map_layers,
        )

    def make_report(
        self,
        strategy_name: str,
        target_form: str,
        source_numbers: tuple[int, ...],
        merge_passes: tuple[MergePass, ...],
        variable_names: tuple[str, ...] = tuple(),
        prime_terms: tuple[str, ...] = tuple(),
        selected_terms: tuple[str, ...] = tuple(),
        coverage_table: CoverageTable | None = None,
        map_layers: tuple[MapLayer, ...] = tuple(),
    ) -> ReductionReport:
        """Собирает финальный отчет по одной конкретной минимизации."""
        rendered_terms = tuple(
            self.pattern_to_formula(pattern, variable_names, target_form)
            for pattern in selected_terms
        )
        minimized_formula = self.constant_formula(target_form)
        if rendered_terms:
            minimized_formula = self.join_formula_terms(rendered_terms, target_form)
        return ReductionReport(
            strategy_name=strategy_name,
            target_form=target_form,
            source_numbers=source_numbers,
            prime_terms=prime_terms,
            selected_terms=selected_terms,
            minimized_formula=minimized_formula,
            merge_passes=merge_passes,
            coverage_table=coverage_table,
            map_layers=map_layers,
        )

    def constant_formula(self, target_form: str) -> str:
        """Возвращает булеву константу для пустого набора строк."""
        if target_form == FORM_DISJUNCTION:
            return "0"
        return "1"

    def number_to_pattern(self, number: int, variable_count: int) -> str:
        """Преобразует номер строки в двоичный шаблон фиксированной длины."""
        return format(number, f"0{variable_count}b")

    def pattern_covers(self, pattern: str, number: int) -> bool:
        """Проверяет, покрывает ли шаблон конкретную строку таблицы."""
        bit_text = format(number, f"0{len(pattern)}b")
        for pattern_bit, number_bit in zip(pattern, bit_text, strict=True):
            if pattern_bit == "-":
                continue
            if pattern_bit != number_bit:
                return False
        return True

    def pattern_to_formula(
        self,
        pattern: str,
        variable_names: tuple[str, ...],
        target_form: str,
    ) -> str:
        """Переводит шаблон вида `10-` в логический терм.

        Символ `-` означает «эта переменная устранена при склеивании»
        и потому в результат не попадает.
        """
        literal_list: list[str] = []
        for pattern_bit, variable_name in zip(pattern, variable_names, strict=True):
            if pattern_bit == "-":
                continue
            if target_form == FORM_DISJUNCTION:
                if pattern_bit == "1":
                    literal_list.append(variable_name)
                else:
                    literal_list.append(f"!{variable_name}")
            else:
                if pattern_bit == "1":
                    literal_list.append(f"!{variable_name}")
                else:
                    literal_list.append(variable_name)
        if not literal_list:
            if target_form == FORM_DISJUNCTION:
                return "1"
            return "0"
        if len(literal_list) == 1:
            return literal_list[0]
        join_sign = "&"
        if target_form == FORM_CONJUNCTION:
            join_sign = "|"
        return f"({join_sign.join(literal_list)})"

    def join_formula_terms(
        self,
        term_list: tuple[str, ...],
        target_form: str,
    ) -> str:
        """Склеивает готовые термы в одну итоговую формулу."""
        if target_form == FORM_DISJUNCTION:
            return "|".join(term_list)
        return "&".join(term_list)

    def generate_prime_patterns(
        self,
        source_numbers: tuple[int, ...],
        variable_count: int,
    ) -> tuple[tuple[str, ...], tuple[MergePass, ...]]:
        """Находит простые импликанты через повторяющиеся этапы склеивания."""
        current_terms = self._build_initial_records(source_numbers, variable_count)
        prime_map: dict[str, PatternRecord] = {}
        merge_steps: list[MergePass] = []
        pass_number = 1
        while current_terms:
            merged_pairs, next_terms, leftover_terms = self._merge_round(current_terms)
            for term in leftover_terms:
                prime_map[term.pattern] = term
            merge_steps.append(
                MergePass(
                    pass_number=pass_number,
                    source_terms=tuple(sorted(current_terms)),
                    merged_pairs=tuple(
                        sorted(
                            merged_pairs,
                            key=lambda pair: (
                                pair.left_term,
                                pair.right_term,
                                pair.merged_term,
                            ),
                        )
                    ),
                    produced_terms=tuple(sorted(next_terms)),
                    leftover_terms=tuple(
                        sorted(term.pattern for term in leftover_terms)
                    ),
                )
            )
            if not next_terms:
                break
            current_terms = next_terms
            pass_number += 1
        return tuple(sorted(prime_map)), tuple(merge_steps)

    def build_coverage_table(
        self,
        prime_terms: tuple[str, ...],
        source_numbers: tuple[int, ...],
    ) -> CoverageTable:
        """Строит матрицу покрытия «импликанта -> покрываемые строки»."""
        mark_rows: list[tuple[int, ...]] = []
        for pattern in prime_terms:
            mark_rows.append(
                tuple(
                    1 if self.pattern_covers(pattern, number) else 0
                    for number in source_numbers
                )
            )
        return CoverageTable(
            column_numbers=source_numbers,
            row_terms=prime_terms,
            marks=tuple(mark_rows),
        )

    def choose_cover(
        self,
        prime_terms: tuple[str, ...],
        source_numbers: tuple[int, ...],
    ) -> tuple[str, ...]:
        """Выбирает набор импликант, покрывающий все нужные строки.

        Сначала выбираются существенные импликанты,
        затем оставшееся покрывается жадным способом.
        """
        if not source_numbers:
            return tuple()
        coverage_map = {
            pattern: {
                number
                for number in source_numbers
                if self.pattern_covers(pattern, number)
            }
            for pattern in prime_terms
        }
        selected_terms: list[str] = []
        uncovered_numbers = set(source_numbers)
        essential_terms = self._find_essential_terms(coverage_map, source_numbers)
        for pattern in essential_terms:
            if pattern in selected_terms:
                continue
            selected_terms.append(pattern)
            uncovered_numbers -= coverage_map[pattern]
        while uncovered_numbers:
            candidate = self._best_covering_pattern(
                coverage_map,
                uncovered_numbers,
                selected_terms,
            )
            if candidate is None:
                break
            selected_terms.append(candidate)
            uncovered_numbers -= coverage_map[candidate]
        return tuple(selected_terms)

    def _build_initial_records(
        self,
        source_numbers: tuple[int, ...],
        variable_count: int,
    ) -> dict[str, PatternRecord]:
        """Создает исходный набор термов без склеивания."""
        record_map: dict[str, PatternRecord] = {}
        for number in source_numbers:
            pattern = self.number_to_pattern(number, variable_count)
            record_map[pattern] = PatternRecord(
                pattern=pattern,
                covered_numbers=frozenset({number}),
            )
        return record_map

    def _merge_round(
        self,
        record_map: dict[str, PatternRecord],
    ) -> tuple[list[MergePair], dict[str, PatternRecord], tuple[PatternRecord, ...]]:
        """Выполняет один полный проход склеивания."""
        grouped_map = self._group_by_ones(tuple(record_map.values()))
        merged_pairs: list[MergePair] = []
        used_patterns: set[str] = set()
        next_terms: dict[str, PatternRecord] = {}
        for group_number in sorted(grouped_map):
            left_group = grouped_map[group_number]
            right_group = grouped_map.get(group_number + 1, tuple())
            for left_record in left_group:
                for right_record in right_group:
                    merged_record = self._merge_two_records(left_record, right_record)
                    if merged_record is None:
                        continue
                    used_patterns.add(left_record.pattern)
                    used_patterns.add(right_record.pattern)
                    merged_pairs.append(
                        MergePair(
                            left_term=left_record.pattern,
                            right_term=right_record.pattern,
                            merged_term=merged_record.pattern,
                        )
                    )
                    previous_record = next_terms.get(merged_record.pattern)
                    if previous_record is None:
                        next_terms[merged_record.pattern] = merged_record
                    else:
                        next_terms[merged_record.pattern] = PatternRecord(
                            pattern=merged_record.pattern,
                            covered_numbers=frozenset(
                                previous_record.covered_numbers
                                | merged_record.covered_numbers
                            ),
                        )
        leftover_terms = tuple(
            record
            for record in record_map.values()
            if record.pattern not in used_patterns
        )
        return merged_pairs, next_terms, leftover_terms

    def _group_by_ones(
        self,
        records: tuple[PatternRecord, ...],
    ) -> dict[int, tuple[PatternRecord, ...]]:
        """Группирует шаблоны по числу единиц.

        Это классический прием для алгоритма Квайна-Мак-Класки:
        склеивать имеет смысл только соседние группы.
        """
        grouped_map: dict[int, list[PatternRecord]] = {}
        for record in records:
            one_count = record.pattern.count("1")
            grouped_map.setdefault(one_count, []).append(record)
        return {
            group_number: tuple(group_records)
            for group_number, group_records in grouped_map.items()
        }

    def _merge_two_records(
        self,
        left_record: PatternRecord,
        right_record: PatternRecord,
    ) -> PatternRecord | None:
        """Пытается склеить два шаблона, различающихся ровно в одном бите."""
        difference_count = 0
        merged_bits: list[str] = []
        for left_bit, right_bit in zip(
            left_record.pattern,
            right_record.pattern,
            strict=True,
        ):
            if left_bit == right_bit:
                merged_bits.append(left_bit)
                continue
            if left_bit == "-" or right_bit == "-":
                return None
            difference_count += 1
            merged_bits.append("-")
            if difference_count > 1:
                return None
        if difference_count != 1:
            return None
        return PatternRecord(
            pattern="".join(merged_bits),
            covered_numbers=frozenset(
                left_record.covered_numbers | right_record.covered_numbers
            ),
        )

    def _find_essential_terms(
        self,
        coverage_map: dict[str, set[int]],
        source_numbers: tuple[int, ...],
    ) -> tuple[str, ...]:
        """Находит существенные импликанты.

        Импликанта существенная, если существует строка,
        которую покрывает только она одна.
        """
        essential_terms: list[str] = []
        for number in source_numbers:
            covering_terms = [
                pattern
                for pattern, covered_numbers in coverage_map.items()
                if number in covered_numbers
            ]
            if len(covering_terms) != 1:
                continue
            if covering_terms[0] not in essential_terms:
                essential_terms.append(covering_terms[0])
        return tuple(essential_terms)

    def _best_covering_pattern(
        self,
        coverage_map: dict[str, set[int]],
        uncovered_numbers: set[int],
        selected_terms: list[str],
    ) -> str | None:
        """Выбирает наилучший следующий шаблон для жадного покрытия.

        Приоритет:
        1. покрыть как можно больше еще непокрытых строк;
        2. при равенстве использовать меньше литералов;
        3. при полном равенстве брать лексикографически меньший шаблон.
        """
        best_pattern: str | None = None
        best_score = -1
        best_literal_count = 0
        for pattern, covered_numbers in coverage_map.items():
            if pattern in selected_terms:
                continue
            current_score = len(covered_numbers & uncovered_numbers)
            if current_score == 0:
                continue
            literal_count = len(pattern.replace("-", ""))
            if current_score > best_score:
                best_pattern = pattern
                best_score = current_score
                best_literal_count = literal_count
                continue
            if current_score == best_score and literal_count < best_literal_count:
                best_pattern = pattern
                best_literal_count = literal_count
                continue
            if current_score == best_score and literal_count == best_literal_count:
                if best_pattern is None or pattern < best_pattern:
                    best_pattern = pattern
        return best_pattern
