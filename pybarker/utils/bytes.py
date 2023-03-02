

# replace control&nonprintable chars
def _bmask(c):
    if c in [9, 10, 13]:  # \t \r \n
        return 32  # <space>
    return c if c >= 0x20 and c < 0x7F else 46  # .


def _tostr(barray):
    try:
        barray = bytes([_bmask(c) for c in barray])
        return barray.decode("latin1")
    except Exception:
        return str(barray)


# вместо s.hex(" ") с параметром, который только в python 3.8, заменить когда везде python>3.8
def _tohex(barray):
    return " ".join("%02x" % i for i in barray)


# форматирует байтовый дамп в виде
# 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f | .........  .. ..................
# 20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f 30 31 32 33 34 35 36 37 38 39 3a 3b 3c 3d 3e 3f |  !"#$%&'()*+,-./0123456789:;<=>?
# 40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f 50 51 52 53 54 55 56 57 58 59 5a 5b 5c 5d 5e 5f | @ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_
# 60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 6e 6f 70 71 72 73 74 75 76 77 78 79 7a 7b 7c 7d 7e 7f | `abcdefghijklmnopqrstuvwxyz{|}~.
# 80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f 90 91 92 93 94 95 96 97 98 99 9a 9b 9c 9d 9e 9f | ................................
# a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 aa ab ac ad ae af b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ba bb bc bd be bf | ................................
# c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 ca cb cc cd ce cf d0 d1 d2 d3 d4 d5 d6 d7 d8 d9 da db dc dd de df | ................................
# e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 ea eb ec ed ee ef f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 fa fb fc fd fe ff | ................................
# поддерживает: memoryview of bytes (from django binaryfield etc), memoryview of int, bytes, bytearray
def format_bytes_dump(barray, dump_width=32):
    if isinstance(barray, (bytes, bytearray)):  # всё к одному для единообразия, лучше всего в memoryview
        barray = memoryview(barray)
    if isinstance(barray, memoryview):
        # от джанговского формата некоторого защита, когда элементы не int а единичные байты, так проще сразу сконвертить
        if barray.format == "c":
            barray = barray.cast("B")
    rows = []
    for row in range(len(barray) // dump_width + 1):
        brow = barray[dump_width * row:dump_width * row + dump_width]
        if brow:
            rows.append("%s%s | %s" % (_tohex(brow), (" " * 3 * (dump_width - len(brow))), _tostr(brow)))  # html.escape(_tostr(brow.tobytes()))
    return "\n".join(rows)


# обратная операция к format_bytes_dump, может понадобиться для тестов, например
# возвращает байты в виде bytearray (можно напрямую сравнивать с bytes например)
def parse_bytes_dump(dumpstr):
    if dumpstr is None:
        return None
    barray = bytearray()
    for line in dumpstr.split("\n"):
        if "|" in line:
            b, _s = line.split("|", maxsplit=1)
        else:
            b = line  # может без строковой части и без | подсунули, для удобства поддержим
        byt = bytes.fromhex(b)
        barray.extend(byt)
    return barray
