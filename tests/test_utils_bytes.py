import unittest

from pybarker2.utils.bytes import format_bytes_dump, parse_bytes_dump


# b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d
# \x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81
# \x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e
# \x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb
# \xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8
# \xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5
# \xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
def bytes_0_255():
    return bytes([i for i in range(256)])


DUMP_32 = """00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f | .........  .. ..................
20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f 30 31 32 33 34 35 36 37 38 39 3a 3b 3c 3d 3e 3f |  !"#$%&'()*+,-./0123456789:;<=>?
40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f 50 51 52 53 54 55 56 57 58 59 5a 5b 5c 5d 5e 5f | @ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_
60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 6e 6f 70 71 72 73 74 75 76 77 78 79 7a 7b 7c 7d 7e 7f | `abcdefghijklmnopqrstuvwxyz{|}~.
80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f 90 91 92 93 94 95 96 97 98 99 9a 9b 9c 9d 9e 9f | ................................
a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 aa ab ac ad ae af b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ba bb bc bd be bf | ................................
c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 ca cb cc cd ce cf d0 d1 d2 d3 d4 d5 d6 d7 d8 d9 da db dc dd de df | ................................
e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 ea eb ec ed ee ef f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 fa fb fc fd fe ff | ................................"""


DUMP_17 = """00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 | .........  .. ...
11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f 20 21 | ............... !
22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f 30 31 32 | "#$%&'()*+,-./012
33 34 35 36 37 38 39 3a 3b 3c 3d 3e 3f 40 41 42 43 | 3456789:;<=>?@ABC
44 45 46 47 48 49 4a 4b 4c 4d 4e 4f 50 51 52 53 54 | DEFGHIJKLMNOPQRST
55 56 57 58 59 5a 5b 5c 5d 5e 5f 60 61 62 63 64 65 | UVWXYZ[\]^_`abcde
66 67 68 69 6a 6b 6c 6d 6e 6f 70 71 72 73 74 75 76 | fghijklmnopqrstuv
77 78 79 7a 7b 7c 7d 7e 7f 80 81 82 83 84 85 86 87 | wxyz{|}~.........
88 89 8a 8b 8c 8d 8e 8f 90 91 92 93 94 95 96 97 98 | .................
99 9a 9b 9c 9d 9e 9f a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 | .................
aa ab ac ad ae af b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ba | .................
bb bc bd be bf c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 ca cb | .................
cc cd ce cf d0 d1 d2 d3 d4 d5 d6 d7 d8 d9 da db dc | .................
dd de df e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 ea eb ec ed | .................
ee ef f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 fa fb fc fd fe | .................
ff                                                 | ."""


class Test(unittest.TestCase):

    def test_format_bytes_dump(self):
        # memoryview (int, format "B")
        self.assertEqual(format_bytes_dump(memoryview(bytearray(bytes_0_255())), dump_width=32), DUMP_32)
        self.assertEqual(format_bytes_dump(memoryview(bytearray(bytes_0_255())), dump_width=17), DUMP_17)
        # bytes
        self.assertEqual(format_bytes_dump(bytes_0_255(), dump_width=32), DUMP_32)
        self.assertEqual(format_bytes_dump(bytes_0_255(), dump_width=17), DUMP_17)
        # bytearray
        self.assertEqual(format_bytes_dump(bytearray(bytes_0_255()), dump_width=32), DUMP_32)
        self.assertEqual(format_bytes_dump(bytearray(bytes_0_255()), dump_width=17), DUMP_17)
        # memoryview (from django binaryfield etc) with format "c"
        # [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\t', b'\n', b'\x0b', b'\x0c', b'\r', b'\x0e', b'\x0f', b'\x10', b'\x11', b'\x12', b'\x13', b'\x14', b'\x15', b'\x16', b'\x17', b'\x18', b'\x19', b'\x1a', b'\x1b', b'\x1c', b'\x1d', b'\x1e', b'\x1f', b' ', b'!', b'"', b'#', b'$', b'%', b'&', b"'", b'(', b')', b'*', b'+', b',', b'-', b'.', b'/', b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b':', b';', b'<', b'=', b'>', b'?', b'@', b'A', b'B', b'C', b'D', b'E', b'F', b'G', b'H', b'I', b'J', b'K', b'L', b'M', b'N', b'O', b'P', b'Q', b'R', b'S', b'T', b'U', b'V', b'W', b'X', b'Y', b'Z', b'[', b'\\', b']', b'^', b'_', b'`', b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k', b'l', b'm', b'n', b'o', b'p', b'q', b'r', b's', b't', b'u', b'v', b'w', b'x', b'y', b'z', b'{', b'|', b'}', b'~', b'\x7f', b'\x80', b'\x81', b'\x82', b'\x83', b'\x84', b'\x85', b'\x86', b'\x87', b'\x88', b'\x89', b'\x8a', b'\x8b', b'\x8c', b'\x8d', b'\x8e', b'\x8f', b'\x90', b'\x91', b'\x92', b'\x93', b'\x94', b'\x95', b'\x96', b'\x97', b'\x98', b'\x99', b'\x9a', b'\x9b', b'\x9c', b'\x9d', b'\x9e', b'\x9f', b'\xa0', b'\xa1', b'\xa2', b'\xa3', b'\xa4', b'\xa5', b'\xa6', b'\xa7', b'\xa8', b'\xa9', b'\xaa', b'\xab', b'\xac', b'\xad', b'\xae', b'\xaf', b'\xb0', b'\xb1', b'\xb2', b'\xb3', b'\xb4', b'\xb5', b'\xb6', b'\xb7', b'\xb8', b'\xb9', b'\xba', b'\xbb', b'\xbc', b'\xbd', b'\xbe', b'\xbf', b'\xc0', b'\xc1', b'\xc2', b'\xc3', b'\xc4', b'\xc5', b'\xc6', b'\xc7', b'\xc8', b'\xc9', b'\xca', b'\xcb', b'\xcc', b'\xcd', b'\xce', b'\xcf', b'\xd0', b'\xd1', b'\xd2', b'\xd3', b'\xd4', b'\xd5', b'\xd6', b'\xd7', b'\xd8', b'\xd9', b'\xda', b'\xdb', b'\xdc', b'\xdd', b'\xde', b'\xdf', b'\xe0', b'\xe1', b'\xe2', b'\xe3', b'\xe4', b'\xe5', b'\xe6', b'\xe7', b'\xe8', b'\xe9', b'\xea', b'\xeb', b'\xec', b'\xed', b'\xee', b'\xef', b'\xf0', b'\xf1', b'\xf2', b'\xf3', b'\xf4', b'\xf5', b'\xf6', b'\xf7', b'\xf8', b'\xf9', b'\xfa', b'\xfb', b'\xfc', b'\xfd', b'\xfe', b'\xff']
        bmv = memoryview(bytes_0_255())
        bmv = bmv.cast("c")
        self.assertEqual(format_bytes_dump(bmv, dump_width=32), DUMP_32)
        self.assertEqual(format_bytes_dump(bmv, dump_width=17), DUMP_17)

    def test_parse_bytes_dump(self):
        self.assertEqual(parse_bytes_dump(DUMP_32), bytes_0_255())
        self.assertEqual(parse_bytes_dump(DUMP_17), bytes_0_255())
        # 1, 9999
        self.assertEqual(parse_bytes_dump(format_bytes_dump(bytes_0_255(), dump_width=1)), bytes_0_255())
        self.assertEqual(parse_bytes_dump(format_bytes_dump(bytes_0_255(), dump_width=9999)), bytes_0_255())
        # errors
        self.assertEqual(parse_bytes_dump("00 01 02 | хуй"), b"\x00\x01\x02")
        self.assertEqual(parse_bytes_dump("00 01 02 |"), b"\x00\x01\x02")
        self.assertEqual(parse_bytes_dump("00 01 02"), b"\x00\x01\x02")
        with self.assertRaises(ValueError):
            self.assertEqual(parse_bytes_dump("00 01 FU"), b"\x00\x01\xFF")


if __name__ == "__main__":
    unittest.main()
