"""Минимизация через карту Карно.

Здесь функция рассматривается не как набор термов для склеивания,
а как заполненная карта соседних наборов значений.
Однако итоговый результат все равно переводится в те же шаблоны импликант.
"""

from itertools import product

from domain.entities import MapLayer, ReductionBundle, ReductionReport, TruthMatrix
from domain.minimization.base import ReductionSupport
from domain.settings import FORM_CONJUNCTION, FORM_DISJUNCTION, METHOD_MAP


class KarnaughMapEngine:
    """Минимизирует СДНФ и СКНФ с помощью карт Карно."""

    def __init__(self, support: ReductionSupport | None = None) -> None:
        """Сохраняет общий набор операций над шаблонами."""
        self._support = support or ReductionSupport()

    def minimize_pair(self, truth_matrix: TruthMatrix) -> ReductionBundle:
        """Запускает минимизацию картой Карно для обеих форм."""
        map_layers = self._build_layers(truth_matrix)
        return ReductionBundle(
            disjunction_result=self._minimize_one(
                truth_matrix,
                FORM_DISJUNCTION,
                map_layers,
            ),
            conjunction_result=self._minimize_one(
                truth_matrix,
                FORM_CONJUNCTION,
                map_layers,
            ),
        )

    def _minimize_one(
        self,
        truth_matrix: TruthMatrix,
        target_form: str,
        map_layers: tuple[MapLayer, ...],
    ) -> ReductionReport:
        """Минимизирует одну форму и прикладывает построенную карту Карно."""
        source_numbers = self._support.pick_source_numbers(truth_matrix, target_form)
        if not source_numbers:
            return self._support.build_constant_report(
                METHOD_MAP,
                target_form,
                map_layers=map_layers,
            )
        prime_terms = self._collect_map_terms(
            source_numbers,
            len(truth_matrix.variable_names),
        )
        selected_terms = self._support.choose_cover(prime_terms, source_numbers)
        return self._support.make_report(
            strategy_name=METHOD_MAP,
            target_form=target_form,
            source_numbers=source_numbers,
            merge_passes=tuple(),
            variable_names=truth_matrix.variable_names,
            prime_terms=prime_terms,
            selected_terms=selected_terms,
            map_layers=map_layers,
        )

    def _build_layers(self, truth_matrix: TruthMatrix) -> tuple[MapLayer, ...]:
        """Строит один или два слоя карты Карно в зависимости от числа переменных."""
        variable_count = len(truth_matrix.variable_names)
        if variable_count == 0:
            return tuple()
        if variable_count == 5:
            return self._build_five_variable_layers(truth_matrix)
        row_variables, column_variables = self._split_variables(
            truth_matrix.variable_names
        )
        return (
            self._build_layer(
                truth_matrix,
                row_variables,
                column_variables,
                tuple(),
                "all",
            ),
        )

    def _build_five_variable_layers(
        self,
        truth_matrix: TruthMatrix,
    ) -> tuple[MapLayer, ...]:
        """Разбивает карту для 5 переменных на два слоя по последней переменной."""
        row_variables = truth_matrix.variable_names[:2]
        column_variables = truth_matrix.variable_names[2:4]
        layer_variable = truth_matrix.variable_names[4]
        zero_layer = self._build_layer(
            truth_matrix,
            row_variables,
            column_variables,
            ((layer_variable, 0),),
            f"{layer_variable}=0",
        )
        one_layer = self._build_layer(
            truth_matrix,
            row_variables,
            column_variables,
            ((layer_variable, 1),),
            f"{layer_variable}=1",
        )
        return (zero_layer, one_layer)

    def _split_variables(
        self,
        variable_names: tuple[str, ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Делит переменные между строками и столбцами карты."""
        row_size = len(variable_names) // 2
        return variable_names[:row_size], variable_names[row_size:]

    def _build_layer(
        self,
        truth_matrix: TruthMatrix,
        row_variables: tuple[str, ...],
        column_variables: tuple[str, ...],
        fixed_pairs: tuple[tuple[str, int], ...],
        title: str,
    ) -> MapLayer:
        """Строит один конкретный слой карты Карно."""
        row_labels = self._gray_codes(len(row_variables))
        column_labels = self._gray_codes(len(column_variables))
        cell_rows: list[tuple[int, ...]] = []
        for row_code in row_labels:
            row_map = self._code_to_map(row_variables, row_code)
            current_row: list[int] = []
            for column_code in column_labels:
                value_map = dict(row_map)
                value_map.update(self._code_to_map(column_variables, column_code))
                for variable_name, bit_value in fixed_pairs:
                    value_map[variable_name] = bit_value
                number = self._map_to_number(value_map, truth_matrix.variable_names)
                current_row.append(truth_matrix.result_vector[number])
            cell_rows.append(tuple(current_row))
        return MapLayer(
            title=title,
            row_labels=row_labels,
            column_labels=column_labels,
            cells=tuple(cell_rows),
        )

    def _gray_codes(self, bit_count: int) -> tuple[str, ...]:
        """Генерирует коды Грея для строк и столбцов карты Карно."""
        if bit_count == 0:
            return ("",)
        code_list = []
        for number in range(1 << bit_count):
            gray_number = number ^ (number >> 1)
            code_list.append(format(gray_number, f"0{bit_count}b"))
        return tuple(code_list)

    def _code_to_map(
        self,
        variable_names: tuple[str, ...],
        code: str,
    ) -> dict[str, int]:
        """Преобразует код Грея в отображение переменных в биты."""
        return {
            variable_name: int(bit)
            for variable_name, bit in zip(variable_names, code, strict=True)
        }

    def _map_to_number(
        self,
        value_map: dict[str, int],
        variable_names: tuple[str, ...],
    ) -> int:
        """Преобразует отображение значений обратно в номер строки таблицы."""
        number = 0
        variable_count = len(variable_names)
        for position, variable_name in enumerate(variable_names):
            bit = 1 << (variable_count - position - 1)
            if value_map.get(variable_name, 0):
                number |= bit
        return number

    def _collect_map_terms(
        self,
        source_numbers: tuple[int, ...],
        variable_count: int,
    ) -> tuple[str, ...]:
        """Находит все допустимые крупные области карты Карно.

        Перебираются все шаблоны из `0`, `1` и `-`.
        Оставляются только те, которые покрывают непустое подмножество
        целевых строк и не выходят за их пределы.
        """
        source_set = set(source_numbers)
        best_by_cover: dict[frozenset[int], str] = {}
        for bits in product(("0", "1", "-"), repeat=variable_count):
            pattern = "".join(bits)
            covered_numbers = frozenset(
                number
                for number in range(1 << variable_count)
                if self._support.pattern_covers(pattern, number)
            )
            if not covered_numbers:
                continue
            if not covered_numbers.issubset(source_set):
                continue
            previous_pattern = best_by_cover.get(covered_numbers)
            if previous_pattern is None:
                best_by_cover[covered_numbers] = pattern
                continue
            if pattern.count("-") > previous_pattern.count("-"):
                best_by_cover[covered_numbers] = pattern

        candidate_pairs = [
            (pattern, covered_numbers)
            for covered_numbers, pattern in best_by_cover.items()
        ]
        prime_patterns: list[str] = []
        for pattern, covered_numbers in candidate_pairs:
            if self._is_strict_subset(covered_numbers, candidate_pairs):
                continue
            prime_patterns.append(pattern)
        prime_patterns.sort(
            key=lambda pattern: (
                -len(
                    [
                        number
                        for number in source_numbers
                        if self._support.pattern_covers(pattern, number)
                    ]
                ),
                -pattern.count("-"),
                pattern,
            )
        )
        return tuple(prime_patterns)

    def _is_strict_subset(
        self,
        covered_numbers: frozenset[int],
        candidate_pairs: list[tuple[str, frozenset[int]]],
    ) -> bool:
        """Проверяет, является ли область строго вложенной в более крупную."""
        for _, other_numbers in candidate_pairs:
            if covered_numbers == other_numbers:
                continue
            if covered_numbers.issubset(other_numbers):
                return True
        return False
