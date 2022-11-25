import calendar

from datetime import date


# сколько прошло времени в секундах от first до second, может отрицательно, т.е. second-first
def datetime_delta(first, second):
    if not first or not second:
        return 9223372036854775807
    return int((second - first).total_seconds())


# прибавление к указанной дате кол-ва месяцев (если месяцы отрицательные, то вычитание)
def date_plus_months(dt, month):
    y = dt.year + (month // 12)  # для отрицательных может оказаться неинтуитивно: -3//12=-1, -3%12=9 но работает так же корректно в итоге
    m = dt.month + (month % 12)
    if m > 12:
        m = m - 12
        y = y + 1
    if m < 1:
        m = m + 12
        y = y - 1
    days_in_month = calendar.monthrange(y, m)[1]
    d = dt.day
    if d > days_in_month:
        d = days_in_month
    return date(y, m, d)


def age(birthdate):
    """ вычисление возраста по дате """
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
