"""Арифметика целых чисел"""

from config import BIT_WIDTH, DIVISION_FRAC_BITS
from bit_operations import add_bits, compare_bits, shift_left, subtract_bits
from numbers_converter import NumbersConverter


class Calculator:
    """Арифметика целых чисел"""

    @staticmethod
    def add_in_twos(a_dec, b_dec, width=BIT_WIDTH):
        """Сложить в доп. коже"""

        a_bits = NumbersConverter.to_twos(a_dec, width)
        b_bits = NumbersConverter.to_twos(b_dec, width)
        sum_bits, _ = add_bits(a_bits, b_bits)
        sum_dec = NumbersConverter.twos_to_decimal(sum_bits)

        return {
            "a_bin": a_bits,
            "b_bin": b_bits,
            "res_bin": sum_bits,
            "a_dec": a_dec,
            "b_dec": b_dec,
            "res_dec": sum_dec,
        }

    @staticmethod
    def sub_in_twos(a_dec, b_dec, width=BIT_WIDTH):
        """Вычесть в доп. коде"""
        return Calculator.add_in_twos(a_dec, -b_dec, width)

    @staticmethod
    def multiply_in_direct(a_dec, b_dec, width=BIT_WIDTH):
        """Умножить в прямом коде"""
        a_bits = NumbersConverter.to_direct(a_dec, width)
        b_bits = NumbersConverter.to_direct(b_dec, width)

        sign_bit = a_bits[0] ^ b_bits[0]
        a_magnitude = a_bits[1:]
        b_magnitude = b_bits[1:]
        result_magnitude = [0] * (width - 1)

        for index in range(len(a_magnitude) - 1, -1, -1):
            if a_magnitude[index] == 0:
                continue

            shift = len(a_magnitude) - 1 - index
            shifted_bits = shift_left(b_magnitude, shift)
            result_magnitude, _ = add_bits(result_magnitude, shifted_bits)

        result_bits = [sign_bit] + result_magnitude
        result_dec = NumbersConverter.direct_to_decimal(result_bits)

        return {
            "a_bin": a_bits,
            "b_bin": b_bits,
            "res_bin": result_bits,
            "a_dec": a_dec,
            "b_dec": b_dec,
            "res_dec": result_dec,
        }

    @staticmethod
    def divide_in_direct(
        a_dec,
        b_dec,
        width=BIT_WIDTH,
        frac_bits=DIVISION_FRAC_BITS,
    ):
        """Делить в прямом коде"""
        if b_dec == 0:
            raise ZeroDivisionError("Деление на ноль")

        a_bits = NumbersConverter.to_direct(a_dec, width)
        b_bits = NumbersConverter.to_direct(b_dec, width)

        sign_bit = a_bits[0] ^ b_bits[0]

        dividend_bits = a_bits[1:]
        divisor_bits = b_bits[1:]
        remainder = [0] * len(dividend_bits)
        quotient_bits = []

        for next_bit in dividend_bits:
            remainder = remainder[1:] + [next_bit]
            if compare_bits(remainder, divisor_bits) >= 0:
                remainder = subtract_bits(remainder, divisor_bits)
                quotient_bits.append(1)
            else:
                quotient_bits.append(0)

        fractional_bits = []
        for _ in range(frac_bits):
            remainder = remainder[1:] + [0]
            if compare_bits(remainder, divisor_bits) >= 0:
                remainder = subtract_bits(remainder, divisor_bits)
                fractional_bits.append(1)
            else:
                fractional_bits.append(0)

        if all(bit == 0 for bit in quotient_bits) and all(bit == 0 for bit in fractional_bits):
            sign_bit = 0

        result_bits = [sign_bit] + quotient_bits
        integer_value = NumbersConverter.bits_to_unsigned(quotient_bits)
        fraction_value = NumbersConverter.bits_to_unsigned(fractional_bits) / (2 ** frac_bits)
        result_dec = integer_value + fraction_value
        if sign_bit == 1:
            result_dec = -result_dec

        return {
            "a_bin": a_bits,
            "b_bin": b_bits,
            "res_bin": result_bits,
            "res_bin_fixed": (
                f"{NumbersConverter.bits_to_str(result_bits)}."
                f"{NumbersConverter.bits_to_str(fractional_bits)}"
            ),
            "a_dec": a_dec,
            "b_dec": b_dec,
            "res_dec": result_dec,
        }
