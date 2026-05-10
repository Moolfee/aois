"""Лексический анализ логической формулы.

На этом этапе строка пользователя превращается в понятную последовательность
токенов. Это первый обязательный шаг перед синтаксическим анализом,
потому что парсеру намного проще работать не с произвольной строкой,
а с уже распознанными элементами вида «переменная», «оператор», «скобка».
"""

from domain.entities import TokenUnit
from domain.errors import TokenizingError
from domain.settings import (
    ALLOWED_NAMES,
    SIGN_CONJUNCTION,
    SIGN_DISJUNCTION,
    SIGN_EQUIVALENCE,
    SIGN_IMPLICATION,
    SIGN_NEGATION,
    TOKEN_CONJUNCTION,
    TOKEN_DISJUNCTION,
    TOKEN_EQUIVALENCE,
    TOKEN_IMPLICATION,
    TOKEN_LEFT_BRACKET,
    TOKEN_NAME,
    TOKEN_NEGATION,
    TOKEN_RIGHT_BRACKET,
)


class FormulaScanner:
    """Преобразует сырой текст формулы в последовательность токенов."""

    def __init__(self) -> None:
        """Готовит таблицу замен для альтернативных математических символов."""
        self._symbol_aliases = (
            ("¬", SIGN_NEGATION),
            ("∧", SIGN_CONJUNCTION),
            ("∨", SIGN_DISJUNCTION),
            ("→", SIGN_IMPLICATION),
            ("⇒", SIGN_IMPLICATION),
            ("↔", SIGN_EQUIVALENCE),
        )

    def scan(self, expression_text: str) -> tuple[TokenUnit, ...]:
        """Разбивает исходную строку на токены.

        После выполнения этого метода у нас появляется линейная структура,
        пригодная для дальнейшего синтаксического разбора.
        """
        prepared_text = self._prepare_text(expression_text)
        token_list: list[TokenUnit] = []
        index = 0
        while index < len(prepared_text):
            # Разрешаем свободный формат ввода, поэтому пробелы
            # просто пропускаются и не становятся токенами.
            index = self._skip_gap(prepared_text, index)
            if index >= len(prepared_text):
                break
            if prepared_text[index] in ALLOWED_NAMES:
                token = self._scan_name(prepared_text, index)
            else:
                token = self._scan_operator(prepared_text, index)
            token_list.append(token)
            index = token.start_at + len(token.text)
        if not token_list:
            raise TokenizingError("Пустое логическое выражение")
        return tuple(token_list)

    def _prepare_text(self, expression_text: str) -> str:
        """Нормализует выражение перед токенизацией.

        Здесь мы приводим строку к нижнему регистру и заменяем
        математические символы на внутренние обозначения проекта.
        """
        if not expression_text or not expression_text.strip():
            raise TokenizingError("Пустое логическое выражение")
        prepared_text = expression_text.lower()
        for source_symbol, target_symbol in self._symbol_aliases:
            prepared_text = prepared_text.replace(source_symbol, target_symbol)
        return prepared_text

    def _scan_operator(self, expression_text: str, start_at: int) -> TokenUnit:
        """Считывает оператор или скобку из текущей позиции."""
        if expression_text.startswith(SIGN_IMPLICATION, start_at):
            return TokenUnit(TOKEN_IMPLICATION, SIGN_IMPLICATION, start_at)
        symbol = expression_text[start_at]
        if symbol == SIGN_NEGATION:
            return TokenUnit(TOKEN_NEGATION, symbol, start_at)
        if symbol == SIGN_CONJUNCTION:
            return TokenUnit(TOKEN_CONJUNCTION, symbol, start_at)
        if symbol == SIGN_DISJUNCTION:
            return TokenUnit(TOKEN_DISJUNCTION, symbol, start_at)
        if symbol == SIGN_EQUIVALENCE:
            return TokenUnit(TOKEN_EQUIVALENCE, symbol, start_at)
        if symbol == "(":
            return TokenUnit(TOKEN_LEFT_BRACKET, symbol, start_at)
        if symbol == ")":
            return TokenUnit(TOKEN_RIGHT_BRACKET, symbol, start_at)
        raise TokenizingError(f"Недопустимый символ: {symbol}")

    def _scan_name(self, expression_text: str, start_at: int) -> TokenUnit:
        """Считывает имя переменной и сразу проверяет его допустимость."""
        symbol = expression_text[start_at]
        if symbol not in ALLOWED_NAMES:
            raise TokenizingError(f"Недопустимая переменная: {symbol}")
        return TokenUnit(TOKEN_NAME, symbol, start_at)

    def _skip_gap(self, expression_text: str, start_at: int) -> int:
        """Пропускает подряд идущие пробелы и переводы строк."""
        index = start_at
        while index < len(expression_text) and expression_text[index].isspace():
            index += 1
        return index
