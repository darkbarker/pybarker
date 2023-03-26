import time
import unittest
import datetime

from decimal import Decimal

from pybarker.utils.formats.xlsxwriterhelper import make_excel


header = [
    ['A1:B2', '#', {"width": 4}],
    ['C1:C2', 'string', {"width": 12}],
    ['D1:D2', 'decimal', {"width": 15}],

    ['E1:E2', 'bool', {"width": 25}],
    ['F1:F2', 'float', {"width": 25}],
    ['G1:G2', '0', {"width": 25, "cell_format": {"align": "left", "bg_color": "red"}}],

    ['H1:H2', 'datetime.date', {"width": 15}],
    ['I1:I2', 'now()', {"width": 15}],
    ['J1:J2', '0', {"width": 15}],
]


def make_row(index):
    return [
        index + 1,
        666,
        "string",
        Decimal(66.66),

        index % 2 == 0,
        66.66,
        0,

        datetime.date(2022, 1, 1),
        datetime.datetime.now(),
        0,
    ]


def make_data():
    for index in range(3):
        yield make_row(index)


class Test(unittest.TestCase):

    def test_Excel(self):
        output = make_excel(header, {"align": 'center', "valign": 'vcenter'}, 'A3', make_data())
        file = "test.%s.xlsx" % time.time()
        with open(file, "wb") as f:
            f.write(output.read())


if __name__ == "__main__":
    unittest.main()
