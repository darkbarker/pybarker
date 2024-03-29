import re


# обрезка юникодной строки до указанной длины в байтах
def truncate_utf8(unicode_str, maxsize):
    maxsize = 0 if maxsize < 0 else maxsize
    return str(unicode_str.encode('utf-8')[:maxsize], 'utf-8', errors="ignore")


# отличие от truncate_utf8 в попытке сохранить расширение, а отрезать лишнее до него
# расширение == латинское/цифры после точки не длиннее 8 (8 изниоткуда, условно)
# если maxsize меньше длины расширения, то последним подрезается расширение так же с конца
def truncate_utf8_filename(filename, maxsize):
    maxsize = 0 if maxsize < 0 else maxsize
    m = re.match("^.*(\.[a-zA-Z0-9]{1,8})$", filename)
    if m:
        ext = m.group(1)
        len_ext = len(ext)
        if len_ext >= maxsize:  # only ext will remain
            return truncate_utf8(ext, maxsize)
        fname = filename[:-len_ext]
        return truncate_utf8(fname, maxsize - len_ext) + ext
    # if no ext -> truncate_utf8
    return truncate_utf8(filename, maxsize)


def levenshtein_distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n
    current_row = list(range(n + 1))  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


# подрезает текст до указанной макс.длины, вырезает из середины, вставляя заполнитель
# placeholder - чем запонять, по умолчанию "...", может включать "{len}" куда подставится кол-во вырезанных символов
# для None вернёт None, если max_length слишком короткий (не влезает placeholder) то резаться будет просто с конца
def truncate_smart(value: str, max_length: int, placeholder: str="...") -> str:
    if value is None:
        return None
    strlen = len(value)
    if strlen <= max_length:
        return value
    if "{len}" in placeholder:  # for optimization reasons
        # ...{len}...
        _placeholder_tmpl = placeholder
        # rough estimate of extra symbols -> rough phlen
        phlen0 = len(_placeholder_tmpl.format(len=(strlen - max_length)))
        placeholder = _placeholder_tmpl.format(len=(strlen - max_length + phlen0))
        phlen1 = len(placeholder)
        if phlen0 != phlen1:  # there was an increase digits number in the length value
            placeholder = _placeholder_tmpl.format(len=(strlen - max_length + phlen1))
    phlen = len(placeholder)
    if phlen + 2 > max_length:  # 2 = first+last letter
        return value[:max_length]  # dumb truncate
    halflen = (max_length - phlen) // 2
    return value[:halflen] + placeholder + value[-(max_length - phlen - halflen):]  # not "-halflen" because may be //2-rounding


def unicode_strike(text: str) -> str:
    """ зачёркивание текста юникодом """
    return "\u0336".join(text) + "\u0336" if text else text
