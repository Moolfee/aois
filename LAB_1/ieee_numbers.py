"""Представление числа IEEE-754"""

from config import IEEE_EXP_BITS, IEEE_MANTISSA_BITS, IEEE_TOTAL_BITS
from exceptions import (
    IEEEOverflowError,
    InvalidIEEEBitsError,
    InvalidIEEEInputError,
    UnsupportedIEEEValueError,
)
from numbers_converter import NumbersConverter


class IEEENumber:
    """Представление числа в IEEE"""

    def __init__(self, bits):
        if len(bits) != IEEE_TOTAL_BITS:
            raise InvalidIEEEBitsError("IEEE-число должно содержать ровно 32 бита")
        for bit in bits:
            if bit not in (0, 1):
                raise InvalidIEEEBitsError("IEEE-число должно состоять только из 0 и 1")
        self.bits = bits[:]

    @staticmethod
    def _gcd(a, b):
        """Найти наибольший общий делитель двух чисел"""
        while b != 0:
            a, b = b, a % b
        return a

    @staticmethod
    def _reduce_fraction(numerator, denominator):
        """Сократить дробь"""
        if numerator == 0:
            return 0, 1
        divisor = IEEENumber._gcd(numerator, denominator)
        return numerator // divisor, denominator // divisor

    @staticmethod
    def _digits_to_int(text):
        """Преобразовать строку из цифр в целое число"""
        if not text:
            raise InvalidIEEEInputError("ожидалось число")

        result = 0
        for symbol in text:
            if symbol < "0" or symbol > "9":
                raise InvalidIEEEInputError("ожидалось число")
            result = result * 10 + (ord(symbol) - ord("0"))
        return result

    @staticmethod
    def _unsigned_to_decimal_string(value):
        """Преобразовать неотрицательное целое число в десятичную строку"""
        if value == 0:
            return "0"

        digits = []
        while value > 0:
            digits.append(chr(ord("0") + value % 10))
            value //= 10
        digits.reverse()
        return "".join(digits)

    @staticmethod
    def _pow10(power):
        """Вычислить 10 в заданной степени без готовых преобразований"""
        result = 1
        for _ in range(power):
            result *= 10
        return result

    @classmethod
    def _parse_decimal_string(cls, raw_value):
        """Разобрать десятичную строку в знак, числитель и знаменатель"""
        text = raw_value.strip()
        if not text:
            raise InvalidIEEEInputError("ожидалось число")

        sign_bit = 0
        if text[0] in "+-":
            sign_bit = 1 if text[0] == "-" else 0
            text = text[1:]

        if not text:
            raise InvalidIEEEInputError("после знака должно быть число")

        exponent_value = 0
        exponent_index = -1
        for index, symbol in enumerate(text):
            if symbol in "eE":
                exponent_index = index
                break

        if exponent_index != -1:
            mantissa_text = text[:exponent_index]
            exponent_text = text[exponent_index + 1 :]
            if not exponent_text:
                raise InvalidIEEEInputError("после e должен идти показатель степени")

            exponent_sign = 1
            if exponent_text[0] in "+-":
                exponent_sign = -1 if exponent_text[0] == "-" else 1
                exponent_text = exponent_text[1:]

            exponent_value = exponent_sign * cls._digits_to_int(exponent_text)
        else:
            mantissa_text = text

        dot_count = 0
        for symbol in mantissa_text:
            if symbol == ".":
                dot_count += 1
        if dot_count > 1:
            raise InvalidIEEEInputError("число не может содержать несколько точек")

        if "." in mantissa_text:
            integer_part, fractional_part = mantissa_text.split(".", 1)
        else:
            integer_part, fractional_part = mantissa_text, ""

        if not integer_part and not fractional_part:
            raise InvalidIEEEInputError("ожидались десятичные цифры")

        all_digits = integer_part + fractional_part
        numerator = cls._digits_to_int(all_digits) if all_digits else 0
        denominator = cls._pow10(len(fractional_part))

        if exponent_value > 0:
            numerator *= cls._pow10(exponent_value)
        elif exponent_value < 0:
            denominator *= cls._pow10(-exponent_value)

        numerator, denominator = cls._reduce_fraction(numerator, denominator)
        return sign_bit, numerator, denominator

    @staticmethod
    def _compare_with_power_of_two(numerator, denominator, exponent):
        """
            Сравнить дробь numerator/denominator с 2**exponent 
            (между какими степенями двойки находится число)
        """
        if exponent >= 0:
            left = numerator
            right = denominator << exponent
        else:
            left = numerator << (-exponent)
            right = denominator

        if left > right:
            return 1
        if left < right:
            return -1
        return 0

    @classmethod
    def _floor_log2_fraction(cls, numerator, denominator):
        """Найти целую часть логарифма по основанию 2 для дроби"""
        estimate = numerator.bit_length() - denominator.bit_length()

        while cls._compare_with_power_of_two(numerator, denominator, estimate) < 0:
            estimate -= 1

        while cls._compare_with_power_of_two(numerator, denominator, estimate + 1) >= 0:
            estimate += 1

        return estimate

    @staticmethod
    def _round_divide_even(numerator, denominator):
        """Разделить с округлением к ближайшему чётному"""
        quotient = numerator // denominator
        remainder = numerator % denominator
        doubled_remainder = remainder * 2

        if doubled_remainder > denominator:
            return quotient + 1
        if doubled_remainder < denominator:
            return quotient
        if quotient % 2 == 1:
            return quotient + 1
        return quotient

    @classmethod
    def _round_fraction_times_power_of_two(cls, numerator, denominator, power):
        """Округлить значение numerator/denominator * 2**power до целого"""
        if power >= 0:
            scaled_numerator = numerator << power
            scaled_denominator = denominator
        else:
            scaled_numerator = numerator
            scaled_denominator = denominator << (-power)
        return cls._round_divide_even(scaled_numerator, scaled_denominator)

    @classmethod
    def from_fraction(cls, sign_bit, numerator, denominator):
        """Собрать binary32 из знака и обычной дроби"""
        if denominator <= 0:
            raise InvalidIEEEInputError("знаменатель должен быть положительным")
        if numerator < 0:
            raise InvalidIEEEInputError("числитель должен быть неотрицательным")

        if numerator == 0:
            return cls([sign_bit] + [0] * (IEEE_TOTAL_BITS - 1))

        numerator, denominator = cls._reduce_fraction(numerator, denominator)
        exponent = cls._floor_log2_fraction(numerator, denominator)

        if exponent > 127:
            raise IEEEOverflowError("число не помещается в IEEE-754 binary32")

        if exponent >= -126:
            significand = cls._round_fraction_times_power_of_two(
                numerator,
                denominator,
                IEEE_MANTISSA_BITS - exponent,
            )

            if significand >= (1 << (IEEE_MANTISSA_BITS + 1)):
                significand >>= 1
                exponent += 1

            if exponent > 127:
                raise IEEEOverflowError("число не помещается в IEEE-754 binary32")

            exponent_bits = NumbersConverter.abs_to_bits(exponent + 127, IEEE_EXP_BITS)
            mantissa_bits = NumbersConverter.abs_to_bits(
                significand - (1 << IEEE_MANTISSA_BITS),
                IEEE_MANTISSA_BITS,
            )
            return cls([sign_bit] + exponent_bits + mantissa_bits)

        mantissa = cls._round_fraction_times_power_of_two(numerator, denominator, 149)

        if mantissa == 0:
            return cls([sign_bit] + [0] * (IEEE_TOTAL_BITS - 1))

        if mantissa >= (1 << IEEE_MANTISSA_BITS):
            exponent_bits = NumbersConverter.abs_to_bits(1, IEEE_EXP_BITS)
            mantissa_bits = [0] * IEEE_MANTISSA_BITS
            return cls([sign_bit] + exponent_bits + mantissa_bits)

        exponent_bits = [0] * IEEE_EXP_BITS
        mantissa_bits = NumbersConverter.abs_to_bits(mantissa, IEEE_MANTISSA_BITS)
        return cls([sign_bit] + exponent_bits + mantissa_bits)

    @classmethod
    def from_string(cls, raw_value):
        """Создать binary32 из десятичной строки"""
        sign_bit, numerator, denominator = cls._parse_decimal_string(raw_value)
        return cls.from_fraction(sign_bit, numerator, denominator)

    def to_fraction(self):
        """Разобрать 32 бита в знак, числитель и знаменатель"""
        exponent_value = NumbersConverter.bits_to_unsigned(
            self.bits[1 : 1 + IEEE_EXP_BITS]
        )
        mantissa_value = NumbersConverter.bits_to_unsigned(
            self.bits[1 + IEEE_EXP_BITS :]
        )

        if exponent_value == (1 << IEEE_EXP_BITS) - 1:
            raise UnsupportedIEEEValueError("special IEEE values не поддерживаются")

        if exponent_value == 0:
            if mantissa_value == 0:
                return self.bits[0], 0, 1
            numerator = mantissa_value
            denominator = 1 << 149
            numerator, denominator = self._reduce_fraction(numerator, denominator)
            return self.bits[0], numerator, denominator

        exponent = exponent_value - 127 - IEEE_MANTISSA_BITS
        numerator = (1 << IEEE_MANTISSA_BITS) + mantissa_value
        denominator = 1

        if exponent >= 0:
            numerator <<= exponent
        else:
            denominator <<= (-exponent)

        numerator, denominator = self._reduce_fraction(numerator, denominator)
        return self.bits[0], numerator, denominator

    def to_decimal_string(self):
        """Преобразовать binary32 в десятичную строку вручную"""
        sign_bit, numerator, denominator = self.to_fraction()

        if numerator == 0:
            return "-0" if sign_bit == 1 else "0"

        integer_part = numerator // denominator
        remainder = numerator % denominator

        decimal_text = self._unsigned_to_decimal_string(integer_part)
        if remainder != 0:
            fractional_digits = []
            while remainder != 0:
                remainder *= 10
                digit = remainder // denominator
                remainder %= denominator
                fractional_digits.append(chr(ord("0") + digit))
            decimal_text = decimal_text + "." + "".join(fractional_digits)

        if sign_bit == 1:
            return "-" + decimal_text
        return decimal_text
