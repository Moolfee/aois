"""CLI интерфейс"""

from bcd_excess3_calculator import BCDCalculator
from calculator import Calculator
from config import BIT_WIDTH, DIVISION_FRAC_BITS
from exceptions import InvalidMenuChoiceError, Lab1Error
from ieee_calculator import IEEECalculator
from ieee_numbers import IEEENumber
from numbers_converter import NumbersConverter


class Menu:
    """Главное меню для вызовафункций"""

    def __init__(self):
        self.ieee_calculator = IEEECalculator()

    def run(self):
        while True:
            self.print_menu()
            choice = input("Выберите пункт: ").strip()

            if choice == "0":
                print("Выход.")
                return

            try:
                self.handle_choice(choice)
            except (ValueError, Lab1Error) as error:
                print(f"Ошибка: {error}")
            except ZeroDivisionError:
                print("Ошибка: деление на 0")

    @staticmethod
    def print_menu():
        """Вывод списка действий"""
        print("\n===== LAB_1 МЕНЮ =====")
        print("1.  Перевод 10 -> прямой, обратный и дополнительный код")
        print("2.  Сложение двух чисел в дополнительном коде")
        print("3.  Вычитание через A + (-B) в дополнительном коде")
        print("4.  Умножение двух чисел в прямом коде")
        print("5.  Деление двух чисел в прямом коде")
        print("6.  IEEE-754 binary32: сложение")
        print("7.  IEEE-754 binary32: вычитание")
        print("8.  IEEE-754 binary32: умножение")
        print("9.  IEEE-754 binary32: деление")
        print("10. Сложение двух чисел в Excess-3")
        print("0.  Выход")

    def handle_choice(self, choice):
        """Хэндлер выбора действий"""
        handlers = {
            "1": self._show_codes,
            "2": self._add_in_twos,
            "3": self._subtract_in_twos,
            "4": self._multiply_in_direct,
            "5": self._divide_in_direct,
            "6": self._ieee_add,
            "7": self._ieee_subtract,
            "8": self._ieee_multiply,
            "9": self._ieee_divide,
            "10": self._bcd_add,
        }
        handler = handlers.get(choice)
        if handler is None:
            raise InvalidMenuChoiceError("неизвестный пункт меню")
        handler()

    @staticmethod
    def _input_int(prompt):
        """Ввод целого числа"""
        return int(input(prompt).strip())

    @staticmethod
    def _input_ieee(prompt):
        return input(prompt).strip()

    @staticmethod
    def _input_bcd_number(prompt):
        """Ввод десятичного числа для Excess-3"""
        return input(prompt).strip()

    @staticmethod
    def _print_integer_result(title, result):
        """Единый формат печати для целочисленных операций."""
        print(f"\n{title}")
        print(f"Первое число: {result['a_dec']}")
        print(f"Код:          {NumbersConverter.bits_to_str(result['a_bin'])}")
        print(f"Второе число: {result['b_dec']}")
        print(f"Код:          {NumbersConverter.bits_to_str(result['b_bin'])}")
        print(f"Результат:    {result['res_dec']}")

        if "res_bin_fixed" in result:
            print(f"Код:          {result['res_bin_fixed']}")
        else:
            print(f"Код:          {NumbersConverter.bits_to_str(result['res_bin'])}")

    def _show_codes(self):
        """Показать прямой, обратный и дополнительный код числа"""
        number = self._input_int("Введите число (10-ый формат): ")
        direct = NumbersConverter.to_direct(number, BIT_WIDTH)
        ones = NumbersConverter.to_ones(number, BIT_WIDTH)
        twos = NumbersConverter.to_twos(number, BIT_WIDTH)

        print("\nКОДЫ")
        print("Число:", number)
        print("Прямой:        ", NumbersConverter.bits_to_str(direct))
        print("Обратный:      ", NumbersConverter.bits_to_str(ones))
        print("Дополнительный:", NumbersConverter.bits_to_str(twos))

    def _add_in_twos(self):
        """Выполнить сложение двух целых в дополнительном коде"""
        left = self._input_int("Введите A: ")
        right = self._input_int("Введите B: ")
        result = Calculator.add_in_twos(left, right, BIT_WIDTH)
        self._print_integer_result("СЛОЖЕНИЕ В ДОП. КОДЕ", result)

    def _subtract_in_twos(self):
        """Выполнить вычитание через A + (-B)"""
        left = self._input_int("Введите A: ")
        right = self._input_int("Введите B: ")
        result = Calculator.sub_in_twos(left, right, BIT_WIDTH)
        self._print_integer_result("ВЫЧИТАНИЕ В ДОП. КОДЕ", result)

    def _multiply_in_direct(self):
        """Выполнить умножение в прямом коде"""
        left = self._input_int("Введите A: ")
        right = self._input_int("Введите B: ")
        result = Calculator.multiply_in_direct(left, right, BIT_WIDTH)
        self._print_integer_result("УМНОЖЕНИЕ В ПРЯМОМ КОДЕ", result)

    def _divide_in_direct(self):
        """Выполнить деление в прямом коде"""
        left = self._input_int("Введите A: ")
        right = self._input_int("Введите B: ")
        result = Calculator.divide_in_direct(left, right, BIT_WIDTH, DIVISION_FRAC_BITS)
        self._print_integer_result("ДЕЛЕНИЕ В ПРЯМОМ КОДЕ", result)

    def _ieee_operation(self, title, operation):
        """Общий шаблон для четырёх IEEE-операций"""
        left_raw = self._input_ieee("Введите первое число: ")
        right_raw = self._input_ieee("Введите второе число: ")

        left = IEEENumber.from_string(left_raw)
        right = IEEENumber.from_string(right_raw)
        result = operation(left, right)

        print(f"\n{title}")
        print(f"Первое число: {left.to_decimal_string()}")
        print(f"IEEE-754:     {NumbersConverter.bits_to_str(left.bits)}")
        print(f"Второе число: {right.to_decimal_string()}")
        print(f"IEEE-754:     {NumbersConverter.bits_to_str(right.bits)}")
        print(f"Результат:    {result.to_decimal_string()}")
        print(f"IEEE-754:     {NumbersConverter.bits_to_str(result.bits)}")

    def _ieee_add(self):
        """IEEE-754 сложение"""
        self._ieee_operation("IEEE-754 СЛОЖЕНИЕ", self.ieee_calculator.add)

    def _ieee_subtract(self):
        """IEEE-754 вычитание"""
        self._ieee_operation("IEEE-754 ВЫЧИТАНИЕ", self.ieee_calculator.subtract)

    def _ieee_multiply(self):
        """IEEE-754 умножение"""
        self._ieee_operation("IEEE-754 УМНОЖЕНИЕ", self.ieee_calculator.multiply)

    def _ieee_divide(self):
        """IEEE-754 деление"""
        self._ieee_operation("IEEE-754 ДЕЛЕНИЕ", self.ieee_calculator.divide)

    @staticmethod
    def _format_excess3(dec_value, bits):
        """Красивый вывод BCD"""
        grouped = []
        for index in range(0, len(bits), 4):
            grouped.append("".join(str(bit) for bit in bits[index : index + 4]))
        result = " ".join(grouped)
        if dec_value < 0 and result:
            return f"-{result}"
        return result

    def _bcd_add(self):
        """Сложить два числа в Excess-3"""
        left = self._input_bcd_number("Введите A: ")
        right = self._input_bcd_number("Введите B: ")

        calculator = BCDCalculator()
        result = calculator.add(left, right)

        print("\nBCD-СЛОЖЕНИЕ (EXCESS-3)")
        print(f"Первое число: {result['a_dec']}")
        print(f"BCD-код:      {self._format_excess3(result['a_dec'], result['a_bits'])}")
        print(f"Второе число: {result['b_dec']}")
        print(f"BCD-код:      {self._format_excess3(result['b_dec'], result['b_bits'])}")
        print(f"Результат:    {result['res_dec']}")
        print(f"BCD-код:      {self._format_excess3(result['res_dec'], result['res_bits'])}")
