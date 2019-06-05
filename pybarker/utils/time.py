

# сколько прошло времени в секундах от first до second, может отрицательно, т.е. second-first
def datetime_delta(first, second):
    if not first or not second:
        return 9223372036854775807
    return int((second - first).total_seconds())
