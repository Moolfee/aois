"""Сложение десятичных чисел в коде Excess-3"""

from exceptions import InvalidBCDDigitError
from bit_operations import add_bits
from numbers_converter import NumbersConverter


class BCDCalculator:
    """Калькулятор для Excess-3"""

    DIGIT_TO_BITS = {
        digit: tuple()
        for digit in range(10)
    }

    for digit in range(10):
        bits = NumbersConverter.abs_to_bits(digit + 3, 4)
        DIGIT_TO_BITS[digit] = tuple(bits)

    def encode_digit(self, digit):
        """Закодировать одну десятичную цифру в 4 бита Excess-3"""
        if digit not in self.DIGIT_TO_BITS:
            raise InvalidBCDDigitError(f"digit is not supported: {digit}")
        return list(self.DIGIT_TO_BITS[digit])

    def encode_number(self, raw_number):
        """Преобразовать строку из цифр в список BCD битов"""
        digits = self._normalize_decimal_string(raw_number)
        result = []
        for digit_char in digits:
            result.extend(self.encode_digit(int(digit_char)))
        return result

    def add(self, left_raw, right_raw):
        """Сложить два десятичных числа в коде Excess-3"""
        left_value = self._to_int(left_raw)
        right_value = self._to_int(right_raw)
        left_sign = -1 if left_value < 0 else 1
        right_sign = -1 if right_value < 0 else 1

        left_digits = self._normalize_decimal_string(left_raw)
        right_digits = self._normalize_decimal_string(right_raw)
        left_bits = self.encode_number(left_digits)
        right_bits = self.encode_number(right_digits)

        if left_sign == right_sign:
            result_digits = self._add_digit_strings(left_digits, right_digits)
            result_sign = left_sign
        else:
            comparison = self._compare_digit_strings(left_digits, right_digits)
            if comparison == 0:
                result_digits = "0"
                result_sign = 1
            elif comparison > 0:
                result_digits = self._subtract_digit_strings(left_digits, right_digits)
                result_sign = left_sign
            else:
                result_digits = self._subtract_digit_strings(right_digits, left_digits)
                result_sign = right_sign

        result_bits = self.encode_number(result_digits)
        result_value = self._digits_to_int(result_digits)
        if result_sign < 0 and result_digits != "0":
            result_value = -result_value

        return {
            "a_dec": left_value,
            "b_dec": right_value,
            "res_dec": result_value,
            "a_bits": left_bits,
            "b_bits": right_bits,
            "res_bits": result_bits,
        }

    def _add_digit_strings(self, left_digits, right_digits):
        """Сложить два неотрицательных числа поразрядно в Excess-3"""
        max_len = max(len(left_digits), len(right_digits))
        left_digits = left_digits.zfill(max_len)
        right_digits = right_digits.zfill(max_len)

        carry = 0
        result_codes = []

        for index in range(max_len - 1, -1, -1):
            left_code = self.encode_digit(int(left_digits[index]))
            right_code = self.encode_digit(int(right_digits[index]))
            corrected_code, carry = self._add_excess3_digits(left_code, right_code, carry)
            result_codes.append(corrected_code)

        if carry == 1:
            result_codes.append(self.encode_digit(1))

        result_codes.reverse()
        result_digits = []
        for code in result_codes:
            result_digits.append(str(self._decode_digit(code)))
        return self._trim_leading_zeros("".join(result_digits))

    def _add_excess3_digits(self, left_code, right_code, carry_in):
        """Сложить два 4-битных Excess-3 кода и входной перенос"""
        partial_sum, carry_out = add_bits(left_code, right_code)
        if carry_in == 1:
            partial_sum, extra_carry = add_bits(partial_sum, [0, 0, 0, 1])
            if extra_carry == 1:
                carry_out = 1

        code_value = NumbersConverter.bits_to_unsigned(partial_sum)
        if carry_out == 1:
            corrected_value = code_value + 3
        else:
            corrected_value = code_value - 3

        corrected_code = NumbersConverter.abs_to_bits(corrected_value, 4)
        return corrected_code, carry_out

    def _decode_digit(self, bits):
        """Преобразовать один Excess-3 код обратно в десятичную цифру"""
        code_value = NumbersConverter.bits_to_unsigned(bits)
        digit = code_value - 3
        if digit < 0 or digit > 9:
            raise InvalidBCDDigitError("получен некорректный Excess-3 код")
        return digit

    @staticmethod
    def _compare_digit_strings(left_digits, right_digits):
        """Сравнить два неотрицательных числа, записанных строками"""
        left_digits = BCDCalculator._trim_leading_zeros(left_digits)
        right_digits = BCDCalculator._trim_leading_zeros(right_digits)

        if len(left_digits) > len(right_digits):
            return 1
        if len(left_digits) < len(right_digits):
            return -1
        if left_digits > right_digits:
            return 1
        if left_digits < right_digits:
            return -1
        return 0

    @staticmethod
    def _subtract_digit_strings(left_digits, right_digits):
        """Вычесть right_digits из left_digits поразрядно"""
        left_digits = left_digits.zfill(max(len(left_digits), len(right_digits)))
        right_digits = right_digits.zfill(len(left_digits))

        borrow = 0
        result_digits = []

        for index in range(len(left_digits) - 1, -1, -1):
            left_digit = ord(left_digits[index]) - ord("0")
            right_digit = ord(right_digits[index]) - ord("0")
            diff = left_digit - right_digit - borrow

            if diff < 0:
                diff += 10
                borrow = 1
            else:
                borrow = 0

            result_digits.append(chr(ord("0") + diff))

        result_digits.reverse()
        return BCDCalculator._trim_leading_zeros("".join(result_digits))

    @staticmethod
    def _to_int(raw_number):
        cleaned = raw_number.strip()
        try:
            return int(cleaned)
        except ValueError as error:
            raise InvalidBCDDigitError("принимается только intager") from error

    @staticmethod
    def _digits_to_int(digits):
        """Преобразовать строку из цифр в целое число вручную."""
        value = 0
        for symbol in digits:
            value = value * 10 + (ord(symbol) - ord("0"))
        return value

    @staticmethod
    def _trim_leading_zeros(digits):
        """Убрать ведущие нули, но оставить один ноль для числа 0."""
        index = 0
        while index < len(digits) - 1 and digits[index] == "0":
            index += 1
        return digits[index:]

    @staticmethod
    def _normalize_decimal_string(raw_number):
        """Проверить, что пользователь ввёл целое число"""
        return str(abs(BCDCalculator._to_int(raw_number)))
