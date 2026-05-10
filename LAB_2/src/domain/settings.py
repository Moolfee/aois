"""Общие константы проекта.

Файл централизует:
1. ограничения лабораторной;
2. внутренние имена токенов;
3. строковые обозначения логических операций;
4. имена режимов минимизации и меню.

Такая структура удобна тем, что смысловые строковые значения
не размазываются по десяткам файлов.
"""

# Допустимые имена переменных по условию задания.
ALLOWED_NAMES = ("a", "b", "c", "d", "e")
# Верхняя граница числа переменных в выражении.
MAX_NAME_COUNT = 5
# Максимальный порядок булевой производной.
MAX_DERIVATIVE_DEPTH = 4

# Типы токенов, которые распознает лексический анализатор.
TOKEN_NAME = "NAME"
TOKEN_NEGATION = "NEGATION"
TOKEN_CONJUNCTION = "CONJUNCTION"
TOKEN_DISJUNCTION = "DISJUNCTION"
TOKEN_IMPLICATION = "IMPLICATION"
TOKEN_EQUIVALENCE = "EQUIVALENCE"
TOKEN_LEFT_BRACKET = "LEFT_BRACKET"
TOKEN_RIGHT_BRACKET = "RIGHT_BRACKET"

SIGN_NEGATION = "!"
SIGN_CONJUNCTION = "&"
SIGN_DISJUNCTION = "|"
SIGN_IMPLICATION = "->"
SIGN_EQUIVALENCE = "~"

# Символьные обозначения булевых констант.
BIT_ZERO = "0"
BIT_ONE = "1"

# Пункты консольного меню.
MENU_STUDY = "1"
MENU_EXIT = "0"

# Имена форм, которые минимизируются в разных алгоритмах.
FORM_DISJUNCTION = "sdnf"
FORM_CONJUNCTION = "sknf"

# Текстовые имена стратегий минимизации для отчета.
METHOD_GLUE = "glue"
METHOD_TABLE = "table"
METHOD_MAP = "map"
