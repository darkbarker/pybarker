import unittest

from pybarker.utils.string import truncate_smart, truncate_utf8, truncate_utf8_filename


class TestUtils(unittest.TestCase):

    def assertTrunc(self, value, max_length, placeholder, optvals):
        if not isinstance(optvals, list):
            optvals = [optvals]
        res = truncate_smart(value, max_length, placeholder=placeholder)
        self.assertIn(res, optvals, "not valid truncate %s to len %s" % (value, max_length))
        if value is not None:
            self.assertIsInstance(res, str)
            self.assertLessEqual(len(res), max_length, "result length > max_length")
            if len(value) >= max_length:
                self.assertEqual(len(res), max_length, "result length != max_length (but len(value) >= max_length)")

    def test_truncate_smart(self):
        self.assertTrunc(None, 666, "...", [None])
        self.assertTrunc("", 666, "...", [""])

        self.assertTrunc("test", 5, "...", ["test"])
        self.assertTrunc("test", 4, "...", ["test"])
        self.assertTrunc("test", 3, "...", ["tes"])
        self.assertTrunc("test", 2, "...", ["te"])
        self.assertTrunc("test", 1, "...", ["t"])
        self.assertTrunc("test", 0, "...", [""])

        self.assertTrunc("test", 3, "…", ["t…t"])
        self.assertTrunc("test", 2, "…", ["te"])

        self.assertTrunc("testtest", 7, "...", ["te...st"])
        self.assertTrunc("testtest", 7, "…", ["tes…est"])
        self.assertTrunc("testtest", 7, "..", ["tes..st", "te..est"])

        self.assertTrunc("test_test", 7, "...", ["te...st"])
        self.assertTrunc("test_test", 7, "…", ["tes…est"])
        self.assertTrunc("test_test", 7, "..", ["tes..st", "te..est"])

        self.assertTrunc("test_test", 8, "...", ["tes...st", "te...est"])
        self.assertTrunc("test_test", 8, "…", ["test…est", "tes…test"])
        self.assertTrunc("test_test", 8, "..", ["tes..est"])

        VAL = "abcdefghijklmnopqrstuvwxyz"

        self.assertTrunc(VAL, 3, "...", ["abc"])
        self.assertTrunc(VAL, 5, "...", ["a...z"])

        PH = "...<{len}>..."

        self.assertTrunc(VAL, 12, PH, ["a...<24>...z"])
        self.assertTrunc(VAL, 14, PH, ["ab...<22>...yz"])
        self.assertTrunc(VAL, 16, PH, ["abc...<20>...xyz"])
        self.assertTrunc(VAL, 18, PH, ["abcd...<18>...wxyz"])
        self.assertTrunc(VAL, 20, PH, ["abcde...<16>...vwxyz"])
        self.assertTrunc(VAL, 22, PH, ["abcdef...<14>...uvwxyz"])
        self.assertTrunc(VAL, 24, PH, ["abcdefg...<12>...tuvwxyz"])

        self.assertTrunc(VAL, 13, PH, ["ab...<23>...z", "a...<23>...yz"])
        self.assertTrunc(VAL, 15, PH, ["abc...<21>...yz", "ab...<21>...xyz"])
        self.assertTrunc(VAL, 17, PH, ["abcd...<19>...xyz", "abc...<19>...wxyz"])
        self.assertTrunc(VAL, 19, PH, ["abcde...<17>...wxyz", "abcd...<17>...vwxyz"])
        self.assertTrunc(VAL, 21, PH, ["abcdef...<15>...vwxyz", "abcde...<15>...uvwxyz"])
        self.assertTrunc(VAL, 23, PH, ["abcdefg...<13>...uvwxyz", "abcdef...<13>...tuvwxyz"])
        self.assertTrunc(VAL, 25, PH, ["abcdefgh...<11>...tuvwxyz", "abcdefg...<11>...stuvwxyz"])

        self.assertTrunc(VAL, 26, PH, [VAL])
        self.assertTrunc(VAL, 11, PH, [VAL[:11]])

    def test_truncate_utf8(self):
        self.assertEqual(truncate_utf8("test", 5), "test")
        self.assertEqual(truncate_utf8("test", 4), "test")
        self.assertEqual(truncate_utf8("test", 2), "te")
        self.assertEqual(truncate_utf8("test", 0), "")

        self.assertEqual(truncate_utf8("тест", 4), "те")  # тест = 8 utf8-bytes
        self.assertEqual(truncate_utf8("тест", 6), "тес")
        self.assertEqual(truncate_utf8("тест", 8), "тест")

        self.assertEqual(truncate_utf8("тест", 3), "т")  # те=4, т=2 utf8-bytes
        self.assertEqual(truncate_utf8("тест", 1), "")

        self.assertEqual(truncate_utf8("test", -1), "")

    def test_truncate_utf8_filename(self):
        self.assertEqual(truncate_utf8_filename("test", 5), "test")
        self.assertEqual(truncate_utf8_filename("test", 4), "test")
        self.assertEqual(truncate_utf8_filename("test", 2), "te")
        self.assertEqual(truncate_utf8_filename("test", 0), "")

        self.assertEqual(truncate_utf8_filename("test.txt", 8), "test.txt")
        self.assertEqual(truncate_utf8_filename("test.txt", 7), "tes.txt")
        self.assertEqual(truncate_utf8_filename("test.txt", 5), "t.txt")
        self.assertEqual(truncate_utf8_filename("test.txt", 4), ".txt")
        self.assertEqual(truncate_utf8_filename("test.txt", 3), ".tx")
        self.assertEqual(truncate_utf8_filename("test.txt", 2), ".t")
        self.assertEqual(truncate_utf8_filename("test.txt", 1), ".")
        self.assertEqual(truncate_utf8_filename("test.txt", 0), "")

        self.assertEqual(truncate_utf8_filename("тест.txt", 12), "тест.txt")
        self.assertEqual(truncate_utf8_filename("тест.txt", 11), "тес.txt")
        self.assertEqual(truncate_utf8_filename("тест.txt", 10), "тес.txt")
        self.assertEqual(truncate_utf8_filename("тест.txt", 6), "т.txt")
        self.assertEqual(truncate_utf8_filename("тест.txt", 5), ".txt")
        self.assertEqual(truncate_utf8_filename("тест.txt", 4), ".txt")
        self.assertEqual(truncate_utf8_filename("test.txt", 3), ".tx")
        self.assertEqual(truncate_utf8_filename("test.txt", 1), ".")
        self.assertEqual(truncate_utf8_filename("test.txt", 0), "")

        # cyr externsion ignore
        self.assertEqual(truncate_utf8_filename("тест.тхт", 12), "тест.т")
        self.assertEqual(truncate_utf8_filename("тест.тхт", 11), "тест.т")
        self.assertEqual(truncate_utf8_filename("тест.тхт", 10), "тест.")
        self.assertEqual(truncate_utf8_filename("тест.тхт", 6), "тес")
        self.assertEqual(truncate_utf8_filename("тест.тхт", 5), "те")
        self.assertEqual(truncate_utf8_filename("тест.тхт", 4), "те")
        self.assertEqual(truncate_utf8_filename("тест.тхт", 3), "т")
        self.assertEqual(truncate_utf8_filename("тест.тхт", 1), "")
        self.assertEqual(truncate_utf8_filename("тест.тхт", 0), "")


if __name__ == "__main__":
    unittest.main()
