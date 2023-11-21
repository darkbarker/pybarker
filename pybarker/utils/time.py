import calendar
import datetime

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


def age(birthdate, targetdate=None) -> int:
    """ вычисление возраста по дате рождения (на указанную дату или now если не передано) """
    today = targetdate or date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


# получение начальной и конечной даты для фильтра год-месяц-день
# параметры должны (не)задаваться последовательно
def get_start_end_dates(year=None, month=None, day=None):
    if year is None:
        start_date = datetime.date(datetime.MINYEAR, 1, 1)
        end_date = datetime.date(datetime.MAXYEAR, 12, 31)
    elif month is None:
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
    elif day is None:
        _fd, cdays = calendar.monthrange(year, month)
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, cdays)
    else:
        start_date = datetime.date(year, month, day)
        end_date = datetime.date(year, month, day)
    return start_date, end_date


# два datetime.date начало-конец превращаем в список (год,месяц) которые лежат межними
# ненулевые, второй не меньше первого
def beg_end_to_mohthrange(beg, end):
    beg = beg.replace(day=1)
    end = end.replace(day=1)
    cal_months = []
    d = beg
    while True:
        cal_months.append((d.year, d.month))
        if d == end:
            break
        _wf, numday = calendar.monthrange(d.year, d.month)
        d += datetime.timedelta(days=numday)
    return cal_months
