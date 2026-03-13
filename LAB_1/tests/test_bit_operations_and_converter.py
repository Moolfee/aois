import pytest

from bit_operations import (
    add_bits,
    add_one,
    compare_bits,
    invert_bits,
    shift_left,
    subtract_bits,
)
from exceptions import InvalidBitOperationError
from numbers_converter import NumbersConverter


def test_bit_operations_cover_main_branches():
    assert invert_bits([1, 0, 1, 0]) == [0, 1, 0, 1]
    assert add_one([0, 0, 1, 1]) == [0, 1, 0, 0]
    assert add_one([1, 1, 1, 1]) == [0, 0, 0, 0]

    result, carry = add_bits([1, 0, 1, 1], [0, 1, 0, 1])
    assert result == [0, 0, 0, 0]
    assert carry == 1

    assert shift_left([1, 0, 1, 1], 0) == [1, 0, 1, 1]
    assert shift_left([1, 0, 1, 1], 2) == [1, 1, 0, 0]
    assert shift_left([1, 0, 1, 1], 4) == [0, 0, 0, 0]

    with pytest.raises(InvalidBitOperationError):
        shift_left([1, 0, 1], -1)

    assert compare_bits([1, 0, 0], [0, 1, 1]) == 1
    assert compare_bits([0, 1, 0], [1, 0, 0]) == -1
    assert compare_bits([1, 0, 1], [1, 0, 1]) == 0

    assert subtract_bits([1, 0, 0, 0], [0, 0, 1, 1]) == [0, 1, 0, 1]
    with pytest.raises(InvalidBitOperationError):
        subtract_bits([0, 0, 1], [1, 0, 0])


def test_numbers_converter_covers_positive_and_negative_codes():
    assert NumbersConverter.abs_to_bits(5, 8) == [0, 0, 0, 0, 0, 1, 0, 1]
    assert NumbersConverter.abs_to_bits(-5, 8) == [0, 0, 0, 0, 0, 1, 0, 1]
    assert NumbersConverter.bits_to_unsigned([1, 0, 1, 0]) == 10

    direct_neg = NumbersConverter.to_direct(-5, 8)
    ones_neg = NumbersConverter.to_ones(-5, 8)
    twos_neg = NumbersConverter.to_twos(-5, 8)

    assert direct_neg == [1, 0, 0, 0, 0, 1, 0, 1]
    assert ones_neg == [1, 1, 1, 1, 1, 0, 1, 0]
    assert twos_neg == [1, 1, 1, 1, 1, 0, 1, 1]

    assert NumbersConverter.to_direct(5, 8) == [0, 0, 0, 0, 0, 1, 0, 1]
    assert NumbersConverter.direct_to_decimal(direct_neg) == -5
    assert NumbersConverter.direct_to_decimal(NumbersConverter.to_direct(7, 8)) == 7
    assert NumbersConverter.twos_to_decimal(NumbersConverter.to_twos(-5, 8)) == -5
    assert NumbersConverter.twos_to_decimal(NumbersConverter.to_twos(5, 8)) == 5
    assert NumbersConverter.bits_to_str([1, 0, 1, 1]) == "1011"
