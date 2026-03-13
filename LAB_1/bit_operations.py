"""Побитовые операции"""

from exceptions import InvalidBitOperationError


def invert_bits(bits):
    """Перевернуть все биты"""
    return [1 - b for b in bits]


def add_one(bits):
    """Прибавить единицу к началу"""
    result = bits.copy()
    carry = 1

    for i in range(len(result) - 1, -1, -1):
        if carry == 0:
            break
        total = result[i] + carry
        result[i] = total % 2
        carry = total // 2
    return result


def add_bits(a, b):
    """Сложить два двоичных числа"""

    result = [0] * len(a)
    carry = 0
    for i in range(len(a) - 1, -1, -1):        
        total = a[i] + b[i] + carry
        result[i] = total % 2
        carry = total // 2
    return result, carry


def shift_left(bits, count=1):
    """Сдвинуть биты влево на count"""
    if count < 0:
        raise InvalidBitOperationError("Количество сдвигов не может быть отрицательным")
    if count == 0:
        return bits.copy()
    if count >= len(bits):
        return [0] * len(bits)
    return bits[count:] + [0] * count


def compare_bits(a, b):
    """Сравнить два модуля бин. числа"""

    for left_bit, right_bit in zip(a, b):
        if left_bit > right_bit:
            return 1
        if left_bit < right_bit:
            return -1
    return 0


def subtract_bits(a, b):
    """Вычесть b из a для модуля бин. ч."""
    if compare_bits(a, b) < 0:
        raise InvalidBitOperationError("Уменьшаемое не может быть меньше вычитаемого")

    result = a.copy()
    borrow = 0
    for index in range(len(result) - 1, -1, -1):
        diff = result[index] - b[index] - borrow
        if diff < 0:
            diff += 2
            borrow = 1
        else:
            borrow = 0
        result[index] = diff
    return result
