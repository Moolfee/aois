"""Use cases for LAB_1."""

from domain.bcd_excess3_calculator import BCDCalculator
from domain.calculator import Calculator
from domain.config import BIT_WIDTH, DIVISION_FRAC_BITS
from domain.ieee_calculator import IEEECalculator
from domain.ieee_numbers import IEEENumber
from domain.numbers_converter import NumbersConverter


class Lab1Service:
    """Application facade for integer, IEEE-754 and Excess-3 operations."""

    def __init__(
        self,
        ieee_calculator: IEEECalculator | None = None,
        bcd_calculator: BCDCalculator | None = None,
    ) -> None:
        self.ieee_calculator = ieee_calculator or IEEECalculator()
        self.bcd_calculator = bcd_calculator or BCDCalculator()

    def get_codes(self, number: int) -> dict[str, int | list[int]]:
        """Build direct, ones' and two's complement codes for a number."""
        return {
            "number": number,
            "direct": NumbersConverter.to_direct(number, BIT_WIDTH),
            "ones": NumbersConverter.to_ones(number, BIT_WIDTH),
            "twos": NumbersConverter.to_twos(number, BIT_WIDTH),
        }

    def add_in_twos(self, left: int, right: int) -> dict[str, int | list[int]]:
        """Add two integers in two's complement."""
        return Calculator.add_in_twos(left, right, BIT_WIDTH)

    def subtract_in_twos(self, left: int, right: int) -> dict[str, int | list[int]]:
        """Subtract integers via A + (-B) in two's complement."""
        return Calculator.sub_in_twos(left, right, BIT_WIDTH)

    def multiply_in_direct(self, left: int, right: int) -> dict[str, int | list[int]]:
        """Multiply integers in sign-magnitude form."""
        return Calculator.multiply_in_direct(left, right, BIT_WIDTH)

    def divide_in_direct(self, left: int, right: int) -> dict[str, int | str | list[int]]:
        """Divide integers in sign-magnitude form."""
        return Calculator.divide_in_direct(
            left,
            right,
            BIT_WIDTH,
            DIVISION_FRAC_BITS,
        )

    def add_ieee(self, left_raw: str, right_raw: str) -> dict[str, IEEENumber]:
        """Add two IEEE-754 binary32 numbers."""
        return self._run_ieee_operation(left_raw, right_raw, self.ieee_calculator.add)

    def subtract_ieee(self, left_raw: str, right_raw: str) -> dict[str, IEEENumber]:
        """Subtract IEEE-754 binary32 numbers."""
        return self._run_ieee_operation(
            left_raw,
            right_raw,
            self.ieee_calculator.subtract,
        )

    def multiply_ieee(self, left_raw: str, right_raw: str) -> dict[str, IEEENumber]:
        """Multiply IEEE-754 binary32 numbers."""
        return self._run_ieee_operation(
            left_raw,
            right_raw,
            self.ieee_calculator.multiply,
        )

    def divide_ieee(self, left_raw: str, right_raw: str) -> dict[str, IEEENumber]:
        """Divide IEEE-754 binary32 numbers."""
        return self._run_ieee_operation(left_raw, right_raw, self.ieee_calculator.divide)

    def add_bcd(self, left_raw: str, right_raw: str) -> dict[str, int | list[int]]:
        """Add two decimal numbers in Excess-3."""
        return self.bcd_calculator.add(left_raw, right_raw)

    def _run_ieee_operation(
        self,
        left_raw: str,
        right_raw: str,
        operation,
    ) -> dict[str, IEEENumber]:
        left = IEEENumber.from_string(left_raw)
        right = IEEENumber.from_string(right_raw)
        return {
            "left": left,
            "right": right,
            "result": operation(left, right),
        }
