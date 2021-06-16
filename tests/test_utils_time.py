import unittest
from datetime import date

from pybarker.utils.time import date_plus_months


class Test(unittest.TestCase):

    def test_date_plus_months(self):
        today = date(2021, 6, 16)
        self.assertEqual(date_plus_months(today, -3), date(2021, 3, 16))
        self.assertEqual(date_plus_months(today, 0), date(2021, 6, 16))
        self.assertEqual(date_plus_months(today, 3), date(2021, 9, 16))

        self.assertEqual(date_plus_months(date(2021, 1, 31), 12), date(2022, 1, 31))
        self.assertEqual(date_plus_months(date(2021, 1, 31), 13), date(2022, 2, 28))
        self.assertEqual(date_plus_months(date(2021, 1, 31), -12), date(2020, 1, 31))
        self.assertEqual(date_plus_months(date(2021, 1, 31), -11), date(2020, 2, 29))


if __name__ == '__main__':
    unittest.main()
