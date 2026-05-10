"""Пользовательские исключения проекта.

Исключения разнесены по группам, чтобы было ясно:
на каком этапе произошла ошибка и как ее показывать пользователю.
Например, ошибка токенизации и ошибка минимизации — это разные ситуации,
поэтому и классы у них разные.
"""

import sys


class Lab2Error(Exception):
    """Базовый класс для всех осмысленных ошибок проекта."""


class MenuError(Lab2Error):
    """Ошибки, относящиеся к работе меню."""


class InvalidMenuSelectionError(MenuError):
    """Пользователь выбрал несуществующий пункт меню."""


class FormulaError(Lab2Error):
    """Общий класс ошибок обработки логической формулы."""


class TokenizingError(FormulaError):
    """Строка не может быть корректно разбита на токены."""


class ParsingError(FormulaError):
    """Из токенов нельзя построить корректное синтаксическое дерево."""


class EvaluationError(FormulaError):
    """Выражение нельзя корректно вычислить на заданном наборе значений."""


class StudyError(Lab2Error):
    """Ошибка на одном из аналитических этапов лабораторной."""


class MinimizationError(StudyError):
    """Ошибка, возникшая во время минимизации."""


sys.modules.setdefault("src.domain.errors", sys.modules[__name__])
