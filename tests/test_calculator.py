import pytest

from calculator import Calculator


def test_add_and_sub_in_twos():
    add_result = Calculator.add_in_twos(7, -3, 8)
    assert add_result["res_dec"] == 4
    assert add_result["a_dec"] == 7
    assert add_result["b_dec"] == -3
    assert len(add_result["res_bin"]) == 8

    sub_result = Calculator.sub_in_twos(7, 3, 8)
    assert sub_result["res_dec"] == 4
    assert sub_result["b_dec"] == -3


def test_multiply_in_direct_for_signs_and_zero():
    assert Calculator.multiply_in_direct(3, 5, 8)["res_dec"] == 15
    assert Calculator.multiply_in_direct(-3, 5, 8)["res_dec"] == -15
    assert Calculator.multiply_in_direct(-3, -5, 8)["res_dec"] == 15
    assert Calculator.multiply_in_direct(0, 7, 8)["res_dec"] == 0


def test_divide_in_direct_for_integer_fraction_and_zero_result():
    integer_result = Calculator.divide_in_direct(8, 2, 8, 5)
    assert integer_result["res_dec"] == 4
    assert integer_result["res_bin_fixed"].endswith(".00000")

    fraction_result = Calculator.divide_in_direct(7, 2, 8, 5)
    assert fraction_result["res_dec"] == 3.5
    assert fraction_result["res_bin_fixed"].endswith(".10000")

    negative_result = Calculator.divide_in_direct(-1, 2, 8, 5)
    assert negative_result["res_dec"] == -0.5

    zero_result = Calculator.divide_in_direct(0, 5, 8, 5)
    assert zero_result["res_dec"] == 0
    assert zero_result["res_bin"][0] == 0


def test_divide_in_direct_raises_on_zero_divisor():
    with pytest.raises(ZeroDivisionError):
        Calculator.divide_in_direct(5, 0, 8, 5)
