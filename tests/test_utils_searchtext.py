import unittest

from pybarker.utils.searchtext import make_orderby_numeric_value, make_search_values


class TestMediaServerUtil(unittest.TestCase):

    def setUp(self):
        pass

    def test_make_orderby_numeric_value(self):
        self.assertIsInstance(make_orderby_numeric_value(1, 1, 'f1 sd 22f f333d 4444'), str)

        self.assertEqual(make_orderby_numeric_value(5, 1, '123456fdsfdf'), '123456fdsfdf')
        self.assertEqual(make_orderby_numeric_value(5, 1, '12345fdsfdf'), '12345fdsfdf')
        self.assertEqual(make_orderby_numeric_value(5, 1, '1234fdsfdf'), '01234fdsfdf')

        self.assertEqual(make_orderby_numeric_value(5, 1, 'fdsfdf123456fdsfdf'), 'fdsfdf123456fdsfdf')
        self.assertEqual(make_orderby_numeric_value(5, 1, 'fdsfdf12345fdsfdf'), 'fdsfdf12345fdsfdf')
        self.assertEqual(make_orderby_numeric_value(5, 1, 'fdsfdf1234fdsfdf'), 'fdsfdf01234fdsfdf')

        self.assertEqual(make_orderby_numeric_value(5, 1, 'fdsfdf123456'), 'fdsfdf123456')
        self.assertEqual(make_orderby_numeric_value(5, 1, 'fdsfdf12345'), 'fdsfdf12345')
        self.assertEqual(make_orderby_numeric_value(5, 1, 'fdsfdf1234'), 'fdsfdf01234')

        self.assertEqual(make_orderby_numeric_value(5, 1, 'hjhfdsfdf'), 'hjhfdsfdf')
        self.assertEqual(make_orderby_numeric_value(5, 1, 'hj'), 'hj')
        self.assertEqual(make_orderby_numeric_value(5, 1, '1234'), '01234')
        self.assertEqual(make_orderby_numeric_value(5, 1, '123456'), '123456')
        self.assertEqual(make_orderby_numeric_value(5, 1, ''), '')

        self.assertEqual(make_orderby_numeric_value(5, 2, '123456fds123456fdf'), '123456fds123456fdf')
        self.assertEqual(make_orderby_numeric_value(5, 2, '12345fdsf12345df'), '12345fdsf12345df')
        self.assertEqual(make_orderby_numeric_value(5, 2, '1234fdsf1234df'), '01234fdsf01234df')

        self.assertEqual(make_orderby_numeric_value(5, 2, 'f1234dsfdf123456'), 'f01234dsfdf123456')
        self.assertEqual(make_orderby_numeric_value(5, 2, 'f1234dsfdf12345'), 'f01234dsfdf12345')
        self.assertEqual(make_orderby_numeric_value(5, 2, 'f1234dsfdf1234'), 'f01234dsfdf01234')

        self.assertEqual(make_orderby_numeric_value(5, 2, 'hjhfdsfdf'), 'hjhfdsfdf')
        self.assertEqual(make_orderby_numeric_value(5, 2, 'hj'), 'hj')
        self.assertEqual(make_orderby_numeric_value(5, 2, '1234'), '01234')
        self.assertEqual(make_orderby_numeric_value(5, 2, '123456'), '123456')
        self.assertEqual(make_orderby_numeric_value(5, 2, ''), '')

        self.assertEqual(make_orderby_numeric_value(5, 1, '123456fds123456fdf'), '123456fds123456fdf')
        self.assertEqual(make_orderby_numeric_value(5, 1, '12345fdsf12345df'), '12345fdsf12345df')
        self.assertEqual(make_orderby_numeric_value(5, 1, '1234fdsf1234df'), '01234fdsf1234df')

    def test_make_search_values(self):
        self.assertEqual(make_search_values("бен"), "ben")
        self.assertEqual(make_search_values("бен бен", "ден"), "benben den")
        self.assertEqual(make_search_values("бен бен", "ден", "ден"), "benben den")
        self.assertEqual(make_search_values("бен бен", "ден", "дэн"), "benben den")

        self.assertEqual(make_search_values("буй"), "bui buj")  # два варианта транслитерации срабатывают
        self.assertEqual(make_search_values("Б. у. Й"), "bui buj")  # два варианта транслитерации срабатывают


if __name__ == '__main__':
    unittest.main()
