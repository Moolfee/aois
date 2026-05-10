"""Форматирование итогового отчета.

Вывод в этом модуле специально сделан отличающимся от примера:
он организован как последовательный технический протокол анализа
в том же порядке, который задан в лабораторной работе.
"""

from domain.entities import CoverageTable, FunctionStudyResult, MapLayer, ReductionReport


class StudyReportPrinter:
    """Собирает текстовый отчет для вывода в консоль."""

    def format(self, study_result: FunctionStudyResult) -> str:
        """Склеивает разделы отчета в порядке из формулировки задания."""
        section_list = [
            self._format_source_expression(study_result),
            self._format_truth_matrix(study_result),
            self._format_canonical_forms(study_result),
            self._format_numeric_forms(study_result),
            self._format_index_form(study_result),
            self._format_post_classes(study_result),
            self._format_polynomial(study_result),
            self._format_redundant_variables(study_result),
            self._format_derivatives(study_result),
            self._format_glue_method(study_result),
            self._format_table_method(study_result),
            self._format_map_method(study_result),
        ]
        return "\n\n".join(section_list)

    def _format_source_expression(self, study_result: FunctionStudyResult) -> str:
        """Показывает исходную функцию и состав переменных."""
        variable_text = ", ".join(study_result.truth_matrix.variable_names)
        return "\n".join(
            [
                "=== 1. ИСХОДНАЯ ФУНКЦИЯ ===",
                f"Записанное выражение: {study_result.expression_text}",
                f"Обнаруженные переменные: {variable_text}",
            ]
        )

    def _format_truth_matrix(self, study_result: FunctionStudyResult) -> str:
        """Форматирует раздел с таблицей истинности."""
        header_parts = ["№"] + list(study_result.truth_matrix.variable_names) + ["f"]
        line_list = ["=== 2. ТАБЛИЦА ИСТИННОСТИ ===", " | ".join(header_parts)]
        for row in study_result.truth_matrix.rows:
            row_bits = [str(row.number)] + [
                "1" if row.values[variable_name] else "0"
                for variable_name in study_result.truth_matrix.variable_names
            ]
            row_bits.append("1" if row.result_value else "0")
            line_list.append(" | ".join(row_bits))
        return "\n".join(line_list)

    def _format_canonical_forms(self, study_result: FunctionStudyResult) -> str:
        """Форматирует канонические формы."""
        return "\n".join(
            [
                "=== 3. СОВЕРШЕННЫЕ ФОРМЫ ===",
                f"Совершенная дизъюнктивная форма: {study_result.canonical_forms.full_disjunction}",
                f"Совершенная конъюнктивная форма: {study_result.canonical_forms.full_conjunction}",
            ]
        )

    def _format_numeric_forms(self, study_result: FunctionStudyResult) -> str:
        """Форматирует числовые формы СДНФ и СКНФ."""
        return "\n".join(
            [
                "=== 4. ЧИСЛОВЫЕ ФОРМЫ ===",
                f"Номера наборов для СДНФ: {study_result.canonical_forms.disjunction_numbers}",
                f"Номера наборов для СКНФ: {study_result.canonical_forms.conjunction_numbers}",
            ]
        )

    def _format_index_form(self, study_result: FunctionStudyResult) -> str:
        """Форматирует индексную форму функции."""
        return "\n".join(
            [
                "=== 5. ИНДЕКСНАЯ ФОРМА ===",
                f"Вектор функции: {study_result.index_presentation.bit_vector}",
                f"Десятичный индекс: {study_result.index_presentation.decimal_value}",
            ]
        )

    def _format_post_classes(self, study_result: FunctionStudyResult) -> str:
        """Форматирует результаты проверки классов Поста."""
        line_list = [
            "=== 6. КЛАССЫ ПОСТА ===",
            f"T0: {self._bool_to_text(study_result.post_summary.keeps_zero)}",
            f"T1: {self._bool_to_text(study_result.post_summary.keeps_one)}",
            f"S : {self._bool_to_text(study_result.post_summary.is_self_dual)}",
            f"M : {self._bool_to_text(study_result.post_summary.is_monotone)}",
            f"L : {self._bool_to_text(study_result.post_summary.is_linear)}",
        ]
        return "\n".join(line_list)

    def _format_polynomial(self, study_result: FunctionStudyResult) -> str:
        """Форматирует полином Жегалкина."""
        return "\n".join(
            [
                "=== 7. ПОЛИНОМ ЖЕГАЛКИНА ===",
                f"Полиномиальная запись: {study_result.polynomial_summary.formula_text}",
                f"Коэффициенты: {study_result.polynomial_summary.coefficients}",
            ]
        )

    def _format_redundant_variables(self, study_result: FunctionStudyResult) -> str:
        """Форматирует список фиктивных переменных."""
        if study_result.redundant_variables:
            variable_text = ", ".join(study_result.redundant_variables)
        else:
            variable_text = "не обнаружены"
        return "\n".join(
            [
                "=== 8. ФИКТИВНЫЕ ПЕРЕМЕННЫЕ ===",
                f"Результат проверки: {variable_text}",
            ]
        )

    def _format_derivatives(self, study_result: FunctionStudyResult) -> str:
        """Форматирует все найденные булевы производные."""
        line_list = ["=== 9. БУЛЕВЫ ПРОИЗВОДНЫЕ ==="]
        derivative_names = sorted(
            study_result.derivatives,
            key=lambda item: (len(item), item),
        )
        for variable_group in derivative_names:
            derivative = study_result.derivatives[variable_group]
            line_list.append(f"[{','.join(variable_group)}]")
            line_list.append(
                f"  Вектор производной: {''.join(str(bit) for bit in derivative.result_vector)}"
            )
            line_list.append(f"  Номера изменяющихся строк: {derivative.changed_rows}")
            line_list.append(f"  Производная в СДНФ: {derivative.full_disjunction}")
            line_list.append(f"  Производная в СКНФ: {derivative.full_conjunction}")
        return "\n".join(line_list)

    def _format_glue_method(self, study_result: FunctionStudyResult) -> str:
        """Форматирует расчетный метод минимизации."""
        return self._format_bundle(
            "=== 10. РАСЧЕТНЫЙ МЕТОД ===",
            study_result.glue_reduction.disjunction_result,
            study_result.glue_reduction.conjunction_result,
        )

    def _format_table_method(self, study_result: FunctionStudyResult) -> str:
        """Форматирует расчетно-табличный метод минимизации."""
        return self._format_bundle(
            "=== 11. РАСЧЕТНО-ТАБЛИЧНЫЙ МЕТОД ===",
            study_result.table_reduction.disjunction_result,
            study_result.table_reduction.conjunction_result,
        )

    def _format_map_method(self, study_result: FunctionStudyResult) -> str:
        """Форматирует минимизацию с картой Карно."""
        return self._format_bundle(
            "=== 12. ТАБЛИЧНЫЙ МЕТОД (КАРТА КАРНО) ===",
            study_result.map_reduction.disjunction_result,
            study_result.map_reduction.conjunction_result,
        )

    def _format_bundle(
        self,
        title: str,
        disjunction_report: ReductionReport,
        conjunction_report: ReductionReport,
    ) -> str:
        """Печатает результаты одного метода отдельно для СДНФ и СКНФ."""
        line_list = [title]
        line_list.extend(
            self._format_reduction_report(
                "Для сокращения СДНФ",
                disjunction_report,
            )
        )
        line_list.extend(
            self._format_reduction_report(
                "Для сокращения СКНФ",
                conjunction_report,
            )
        )
        return "\n".join(line_list)

    def _format_reduction_report(
        self,
        title: str,
        report: ReductionReport,
    ) -> list[str]:
        """Форматирует один конкретный отчет по минимизации."""
        line_list = [
            title,
            f"  Исходные строки: {report.source_numbers}",
            f"  Простые шаблоны: {report.prime_terms}",
            f"  Выбранное покрытие: {report.selected_terms}",
            f"  Минимальная запись: {report.minimized_formula}",
        ]
        line_list.extend(self._format_merge_passes(report))
        line_list.extend(self._format_coverage_table(report.coverage_table))
        line_list.extend(self._format_map_layers(report.map_layers))
        return line_list

    def _format_merge_passes(self, report: ReductionReport) -> list[str]:
        """Печатает этапы склеивания, если они есть."""
        if not report.merge_passes:
            return ["  Этапы склеивания: не используются"]
        line_list: list[str] = []
        for merge_pass in report.merge_passes:
            line_list.append(f"  Шаг склеивания {merge_pass.pass_number}:")
            line_list.append(f"    Входной набор: {merge_pass.source_terms}")
            line_list.append(
                "    Выполненные склейки: "
                + str(
                    tuple(
                        (
                            pair.left_term,
                            pair.right_term,
                            pair.merged_term,
                        )
                        for pair in merge_pass.merged_pairs
                    )
                )
            )
            line_list.append(f"    Не склеились: {merge_pass.leftover_terms}")
            line_list.append(f"    Переходят дальше: {merge_pass.produced_terms}")
        return line_list

    def _format_coverage_table(
        self,
        coverage_table: CoverageTable | None,
    ) -> list[str]:
        """Печатает таблицу покрытия для расчетно-табличного метода."""
        if coverage_table is None:
            return []
        line_list = ["  Матрица покрытия:"]
        line_list.append(
            "    строки -> "
            + " ".join(str(number) for number in coverage_table.column_numbers)
        )
        for row_term, row_marks in zip(
            coverage_table.row_terms,
            coverage_table.marks,
            strict=True,
        ):
            line_list.append(
                f"    {row_term}: {' '.join(str(mark) for mark in row_marks)}"
            )
        return line_list

    def _format_map_layers(self, map_layers: tuple[MapLayer, ...]) -> list[str]:
        """Печатает один или несколько слоев карты Карно."""
        if not map_layers:
            return []
        line_list = ["  Таблица Карно:"]
        for map_layer in map_layers:
            line_list.append(f"    Область {map_layer.title}")
            line_list.append(
                "    Заголовки столбцов: "
                + ", ".join(map_layer.column_labels)
            )
            for row_label, cell_row in zip(
                map_layer.row_labels,
                map_layer.cells,
                strict=True,
            ):
                rendered_row = " ".join(str(bit) for bit in cell_row)
                line_list.append(f"    {row_label} -> {rendered_row}")
        return line_list

    def _bool_to_text(self, value: bool) -> str:
        """Преобразует булево значение в текст `да` / `нет`."""
        if value:
            return "да"
        return "нет"
