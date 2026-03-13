import pytest

from bcd_excess3_calculator import BCDCalculator
from exceptions import InvalidBCDDigitError


def test_bcd_encode_and_decode_helpers():
    calculator = BCDCalculator()

    assert calculator.encode_digit(0) == [0, 0, 1, 1]
    assert calculator.encode_digit(9) == [1, 1, 0, 0]
    assert calculator.encode_number("507") == [
        1, 0, 0, 0,
        0, 0, 1, 1,
        1, 0, 1, 0,
    ]

    with pytest.raises(InvalidBCDDigitError):
        calculator.encode_digit(10)

    with pytest.raises(InvalidBCDDigitError):
        calculator._decode_digit([0, 0, 0, 0])


def test_bcd_add_for_same_and_different_signs():
    calculator = BCDCalculator()

    assert calculator.add("59", "14")["res_dec"] == 73
    assert calculator.add("9", "9")["res_dec"] == 18
    assert calculator.add("-12", "-5")["res_dec"] == -17
    assert calculator.add("-12", "5")["res_dec"] == -7
    assert calculator.add("12", "-5")["res_dec"] == 7
    assert calculator.add("-12", "12")["res_dec"] == 0


def test_bcd_internal_code_helpers():
    calculator = BCDCalculator()
    assert calculator._add_digit_strings("12", "05") == "17"
    assert calculator._compare_digit_strings("12", "05") == 1
    assert calculator._compare_digit_strings("05", "12") == -1
    assert calculator._compare_digit_strings("0012", "12") == 0
    assert calculator._subtract_digit_strings("12", "05") == "7"
    assert calculator._digits_to_int("17") == 17
    assert calculator._trim_leading_zeros("0007") == "7"

    corrected_code, carry = calculator._add_excess3_digits(
        calculator.encode_digit(9),
        calculator.encode_digit(9),
        0,
    )
    assert carry == 1
    assert calculator._decode_digit(corrected_code) == 8


def test_bcd_input_validation():
    calculator = BCDCalculator()

    with pytest.raises(InvalidBCDDigitError):
        calculator.add("abc", "1")

    with pytest.raises(InvalidBCDDigitError):
        calculator._to_int("1.5")
