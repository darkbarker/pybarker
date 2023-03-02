import unittest

from pybarker.utils.numbers import digits_r2l


class Test(unittest.TestCase):

    def test_digits_r2l(self):
        self.assertEqual(list(digits_r2l(1234567890)), [0, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual(list(digits_r2l(10)), [0, 1])
        self.assertEqual(list(digits_r2l(99)), [9, 9])
        self.assertEqual(list(digits_r2l(909)), [9, 0, 9])
        for i in range(10):
            self.assertEqual(list(digits_r2l(i)), [i])
            self.assertEqual(list(digits_r2l(1000 + i)), [i, 0, 0, 1])
            self.assertEqual(list(digits_r2l(1000 + i * 10)), [0, i, 0, 1])
            if i != 0:
                self.assertEqual(list(digits_r2l(1000 * i)), [0, 0, 0, i])
                self.assertEqual(list(digits_r2l(1001 * i)), [i, 0, 0, i])
                self.assertEqual(list(digits_r2l(1111 * i)), [i, i, i, i])


if __name__ == "__main__":
    unittest.main()
