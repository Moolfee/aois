import pytest

from exceptions import (
    IEEEOverflowError,
    InvalidIEEEBitsError,
    InvalidIEEEInputError,
    UnsupportedIEEEValueError,
)
from ieee_calculator import IEEECalculator
from ieee_numbers import IEEENumber


def test_ieee_number_validates_bits():
    with pytest.raises(InvalidIEEEBitsError):
        IEEENumber([0] * 31)

    with pytest.raises(InvalidIEEEBitsError):
        IEEENumber([0] * 31 + [2])


@pytest.mark.parametrize(
    "raw_value",
    ["", "+", "abc", "1..2", "1e", "1e+", "--1"],
)
def test_ieee_rejects_invalid_input_strings(raw_value):
    with pytest.raises(InvalidIEEEInputError):
        IEEENumber.from_string(raw_value)


def test_ieee_from_fraction_validates_arguments():
    with pytest.raises(InvalidIEEEInputError):
        IEEENumber.from_fraction(0, 1, 0)

    with pytest.raises(InvalidIEEEInputError):
        IEEENumber.from_fraction(0, -1, 2)


def test_ieee_handles_normal_subnormal_underflow_and_overflow():
    normal = IEEENumber.from_string("1.5")
    assert normal.to_decimal_string() == "1.5"
    assert "".join(str(bit) for bit in normal.bits) == "00111111110000000000000000000000"

    subnormal = IEEENumber.from_string("1e-45")
    assert subnormal.bits[-1] == 1

    underflow = IEEENumber.from_string("1e-46")
    assert underflow.to_decimal_string() == "0"
    assert all(bit == 0 for bit in underflow.bits)

    negative_zero = IEEENumber.from_fraction(1, 0, 1)
    assert negative_zero.to_decimal_string() == "-0"

    with pytest.raises(IEEEOverflowError):
        IEEENumber.from_string("1e39")


def test_ieee_to_fraction_rejects_special_values():
    bits = [0] + [1] * 8 + [0] * 23
    special = IEEENumber(bits)
    with pytest.raises(UnsupportedIEEEValueError):
        special.to_fraction()


def test_ieee_calculator_operations():
    left = IEEENumber.from_string("1.5")
    right = IEEENumber.from_string("2.25")

    assert IEEECalculator._signed_fraction(left) == (3, 2)
    assert IEEECalculator.add(left, right).to_decimal_string() == "3.75"
    assert IEEECalculator.subtract(IEEENumber.from_string("2.5"), IEEENumber.from_string("1.25")).to_decimal_string() == "1.25"
    assert IEEECalculator.multiply(IEEENumber.from_string("1.5"), IEEENumber.from_string("2")).to_decimal_string() == "3"
    assert IEEECalculator.divide(IEEENumber.from_string("3"), IEEENumber.from_string("2")).to_decimal_string() == "1.5"

    with pytest.raises(ZeroDivisionError):
        IEEECalculator.divide(IEEENumber.from_string("1"), IEEENumber.from_string("0"))
