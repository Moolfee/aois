"""Синтаксический анализ логической формулы.

Модуль реализует рекурсивный спуск: каждый метод отвечает
за один уровень приоритета операций.
Именно здесь строка токенов превращается в дерево выражения.
"""

from domain.entities import SyntaxNode, TokenUnit
from domain.errors import ParsingError
from domain.lexical import FormulaScanner
from domain.settings import (
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


class FormulaTreeBuilder:
    """Строит дерево выражения из потока токенов."""

    def __init__(self, scanner: FormulaScanner | None = None) -> None:
        """Подготавливает анализатор и внутреннее состояние парсера."""
        self._scanner = scanner or FormulaScanner()
        self._tokens: tuple[TokenUnit, ...] = tuple()
        self._position = 0

    def build(self, expression_text: str) -> SyntaxNode:
        """Полностью разбирает выражение и возвращает корень дерева."""
        self._tokens = self._scanner.scan(expression_text)
        self._position = 0
        root = self._parse_equivalence()
        if self._current_token() is not None:
            raise ParsingError("Лишние токены в конце выражения")
        return root

    def _parse_equivalence(self) -> SyntaxNode:
        """Разбирает эквивалентность как операцию наименьшего приоритета."""
        node = self._parse_implication()
        while self._match(TOKEN_EQUIVALENCE):
            right = self._parse_implication()
            node = SyntaxNode(
                operation=SIGN_EQUIVALENCE,
                variable=None,
                children=(node, right),
            )
        return node

    def _parse_implication(self) -> SyntaxNode:
        """Разбирает импликацию.

        Важно: импликация делается правоассоциативной,
        что соответствует стандартной логической интерпретации.
        """
        left = self._parse_disjunction()
        if self._match(TOKEN_IMPLICATION):
            right = self._parse_implication()
            return SyntaxNode(
                operation=SIGN_IMPLICATION,
                variable=None,
                children=(left, right),
            )
        return left

    def _parse_disjunction(self) -> SyntaxNode:
        """Разбирает дизъюнкцию `|`."""
        node = self._parse_conjunction()
        while self._match(TOKEN_DISJUNCTION):
            right = self._parse_conjunction()
            node = SyntaxNode(
                operation=SIGN_DISJUNCTION,
                variable=None,
                children=(node, right),
            )
        return node

    def _parse_conjunction(self) -> SyntaxNode:
        """Разбирает конъюнкцию `&`."""
        node = self._parse_negation()
        while self._match(TOKEN_CONJUNCTION):
            right = self._parse_negation()
            node = SyntaxNode(
                operation=SIGN_CONJUNCTION,
                variable=None,
                children=(node, right),
            )
        return node

    def _parse_negation(self) -> SyntaxNode:
        """Разбирает отрицание `!` как унарную операцию."""
        if self._match(TOKEN_NEGATION):
            operand = self._parse_negation()
            return SyntaxNode(
                operation=SIGN_NEGATION,
                variable=None,
                children=(operand,),
            )
        return self._parse_atom()

    def _parse_atom(self) -> SyntaxNode:
        """Разбирает переменную или выражение в скобках."""
        current = self._current_token()
        if current is None:
            raise ParsingError("Ожидался операнд")
        if current.kind == TOKEN_NAME:
            self._consume()
            return SyntaxNode(operation=None, variable=current.text, children=tuple())
        if current.kind == TOKEN_LEFT_BRACKET:
            self._consume()
            node = self._parse_equivalence()
            if not self._match(TOKEN_RIGHT_BRACKET):
                raise ParsingError("Пропущена закрывающая скобка")
            return node
        raise ParsingError("Ожидался операнд")

    def _current_token(self) -> TokenUnit | None:
        """Возвращает текущий токен без продвижения вперед."""
        if self._position >= len(self._tokens):
            return None
        return self._tokens[self._position]

    def _consume(self) -> TokenUnit:
        """Потребляет текущий токен и сдвигает позицию."""
        current = self._current_token()
        if current is None:
            raise ParsingError("Неожиданный конец выражения")
        self._position += 1
        return current

    def _match(self, token_kind: str) -> bool:
        """Проверяет тип текущего токена и при совпадении пропускает его."""
        current = self._current_token()
        if current is None or current.kind != token_kind:
            return False
        self._position += 1
        return True
