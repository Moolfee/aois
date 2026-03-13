"""Операции над числами IEEE-754 binary32."""

from ieee_numbers import IEEENumber


class IEEECalculator:
    """Арифметика для чисел IEEE-754 binary32"""

    @staticmethod
    def _signed_fraction(number):
        """Получить значение числа как signed дробь numerator/denominator."""
        sign_bit, numerator, denominator = number.to_fraction()
        if sign_bit == 1:
            return -numerator, denominator
        return numerator, denominator

    @staticmethod
    def _to_ieee_number(numerator, denominator):
        """Собрать IEEENumber из signed дроби."""
        sign_bit = 1 if numerator < 0 else 0
        magnitude = -numerator if numerator < 0 else numerator
        return IEEENumber.from_fraction(sign_bit, magnitude, denominator)

    @classmethod
    def add(cls, a, b):
        """Сложить два числа IEEE-754 через дроби."""
        left_num, left_den = cls._signed_fraction(a)
        right_num, right_den = cls._signed_fraction(b)
        numerator = left_num * right_den + right_num * left_den
        denominator = left_den * right_den
        return cls._to_ieee_number(numerator, denominator)

    @classmethod
    def subtract(cls, a, b):
        """Вычесть второе число из первого через дроби."""
        left_num, left_den = cls._signed_fraction(a)
        right_num, right_den = cls._signed_fraction(b)
        numerator = left_num * right_den - right_num * left_den
        denominator = left_den * right_den
        return cls._to_ieee_number(numerator, denominator)

    @classmethod
    def multiply(cls, a, b):
        """Перемножить два числа IEEE-754 через дроби."""
        left_num, left_den = cls._signed_fraction(a)
        right_num, right_den = cls._signed_fraction(b)
        numerator = left_num * right_num
        denominator = left_den * right_den
        return cls._to_ieee_number(numerator, denominator)

    @classmethod
    def divide(cls, a, b):
        """Разделить первое число на второе через дроби."""
        left_num, left_den = cls._signed_fraction(a)
        right_num, right_den = cls._signed_fraction(b)

        if right_num == 0:
            raise ZeroDivisionError("деление на 0")

        numerator = left_num * right_den
        denominator = left_den * (right_num if right_num > 0 else -right_num)

        if right_num < 0:
            numerator = -numerator

        return cls._to_ieee_number(numerator, denominator)
