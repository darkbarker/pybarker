import unittest

from pybarker.utils.files import filename_remove_badchars


class Test(unittest.TestCase):

    def test_filename_remove_badchars(self):
        filename = '\\/:*?"<>|+\0'
        filename = f" a{filename}b "
        filename_i = "a___________b"
        self.assertEqual(filename_remove_badchars(filename), filename_i)


if __name__ == "__main__":
    unittest.main()
