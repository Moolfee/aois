"""Переводы между десятичным и двоичным кодом"""

from config import BIT_WIDTH
from bit_operations import add_one, invert_bits


class NumbersConverter:
    """Методы переводорв между десятичным и двоичными кодами"""

    @staticmethod
    def abs_to_bits(n, width=BIT_WIDTH):
        """Десятичная в двоичный код (модуль)"""

        value = n if n >= 0 else -n
        bits = [0] * width
        for i in range(width - 1, -1, -1):
            bits[i] = value % 2
            value //= 2
        return bits

    @staticmethod
    def bits_to_unsigned(bits):
        """Модуль двоичного в десятичное"""
        result = 0
        for bit in bits:
            result = result * 2 + bit
        return result

    @staticmethod
    def to_direct(n, width=BIT_WIDTH):
        """Десятчнаый в прямой код"""
        sign = 0 if n >= 0 else 1
        magnitude = NumbersConverter.abs_to_bits(n, width - 1)
        return [sign] + magnitude

    @staticmethod
    def direct_to_decimal(bits):
        """Прямой в десятичный"""
        sign = bits[0]
        magnitude = NumbersConverter.bits_to_unsigned(bits[1:])
        if sign == 1:
            return -magnitude
        return magnitude

    @staticmethod
    def to_ones(n, width=BIT_WIDTH):
        """Прямой в обратный код"""
        direct = NumbersConverter.to_direct(n, width)
        if n >= 0:
            return direct
        return [1] + invert_bits(direct[1:])

    @staticmethod
    def to_twos(n, width=BIT_WIDTH):
        """Прямой в дополнительный код."""
        ones = NumbersConverter.to_ones(n, width)
        if n >= 0:
            return ones
        return [1] + add_one(ones[1:])

    @staticmethod
    def twos_to_decimal(bits):
        """Доп. код в десятичный"""
        sign = bits[0]
        if sign == 0:
            return NumbersConverter.bits_to_unsigned(bits)
        magnitude_bits = add_one(invert_bits(bits))
        magnitude = NumbersConverter.bits_to_unsigned(magnitude_bits)
        return -magnitude

    @staticmethod
    def bits_to_str(bits):
        """Вернуть читаемую строку битов"""       
        return "".join(str(bit) for bit in bits)
