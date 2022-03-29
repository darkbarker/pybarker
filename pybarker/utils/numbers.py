import decimal


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
