

# обрезка юникодной строки до указанной длины в байтах
def truncate_utf8(unicode_str, maxsize):
    return str(unicode_str.encode('utf-8')[:maxsize], 'utf-8', errors="ignore")
