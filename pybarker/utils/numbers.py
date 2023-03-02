import decimal
from functools import reduce


# строку в decimal, None в None, принимает и точку и запятую
def cost2decimal(strcost):
    if strcost is None:
        return None
    strcost = strcost.replace(",", ".")
    return decimal.Decimal(strcost)


# парсит целое число штатным методом, но поддерживает дефолтное значение (по умолчанию None)
def int_parse(s, val=None, base=10):
    try:
        return int(s, base)
    except ValueError:
        return val


# Предварительно рассчитанные результаты умножения на 2 с вычетом 9 для больших цифр
# Номер индекса равен числу, над которым проводится операция
LUHN_LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)


# проверка кода на алгоритм луна
# довольно дебильный алгоритм, для референстности взят целиком отсюда: https://ru.wikipedia.org/wiki/Алгоритм_Луна
def check_luhn(code):
    if not isinstance(code, str):
        code = str(code)
    code = reduce(str.__add__, filter(str.isdigit, code))
    evens = sum(int(i) for i in code[-1::-2])
    odds = sum(LUHN_LOOKUP[int(i)] for i in code[-2::-2])
    return ((evens + odds) % 10 == 0)


# видоизменяет переданный code(int), заменяя последнюю цифру на контрольную по алгоритму луна
def patch_luhn(code: int) -> int:
    ssum = sum(digit if n % 2 == 0 else LUHN_LOOKUP[digit] for n, digit in enumerate(digits_r2l(code)))
    ssum = ssum % 10
    lastdig = code % 10
    if ssum <= lastdig:  # при одинаковых числах должен 0 получиться, а не + 10 иначе уже вторая цифра испортится
        code = code - ssum
    else:
        code = code - ssum + 10
    # в данный момент важно что code(orig) // 10 == code // 10
    return code


# возвращает цифрами(int) число(int), справа налево (от младшего разряда к старшему), генератор
def digits_r2l(n: int):
    if n == 0:  # exceptional case (controversial... but probably expected 0 = [0])
        yield 0
    while n > 0:
        yield n % 10
        n = n // 10
