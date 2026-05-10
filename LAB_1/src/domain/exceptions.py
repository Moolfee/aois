"""Пользовательские исключения проекта."""


class Lab1Error(Exception):
    """Базовый класс для всех смысловых ошибок проекта."""


class MenuError(Lab1Error):
    """Ошибки, связанные с работой меню."""


class InvalidMenuChoiceError(MenuError):
    """Пользователь выбрал несуществующий пункт меню."""


class BitOperationError(Lab1Error):
    """Ошибки низкоуровневых побитовых операций."""


class InvalidBitOperationError(BitOperationError):
    """Побитовая операция получила некорректные данные."""


class BCDError(Lab1Error):
    """Ошибки операций с Excess-3."""


class InvalidBCDDigitError(BCDError):
    """Введены некорректные цифры для Excess-3."""


class IEEEError(Lab1Error):
    """Ошибки представления и арифметики IEEE-754."""


class InvalidIEEEInputError(IEEEError):
    """Строка не может быть разобрана как IEEE-число."""


class InvalidIEEEBitsError(IEEEError):
    """Набор битов не является корректным IEEE binary32."""


class UnsupportedIEEEValueError(IEEEError):
    """Запрошено IEEE-значение, которое проект не поддерживает."""


class IEEEOverflowError(IEEEError, OverflowError):
    """Число не помещается в диапазон IEEE-754 binary32."""
