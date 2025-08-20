import unittest

from pybarker.utils.collections import list_difference, subdict


class TestMediaServerUtil(unittest.TestCase):

    def test_subdict(self):
        self.assertEqual(subdict({}, []), {})
        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, []), {})

        self.assertEqual(subdict({}, ["x", "y", "z"]), {})

        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, ["x", "y", "z"]), {})
        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, [None]), {})

        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, ["a"]), {"a": 1})
        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, ["b"]), {"b": {"c": 3}})
        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, ["a", "b"]), {"a": 1, "b": {"c": 3}})

        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, ["a", "x", "y", "z"]), {"a": 1})
        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, ["b", "x", "y", "z"]), {"b": {"c": 3}})
        self.assertEqual(subdict({"a": 1, "b": {"c": 3}}, ["a", "b", "x", "y", "z"]), {"a": 1, "b": {"c": 3}})

    def test_list_difference(self):
        self.assertEqual(list_difference([1, 2, 3, 4], [1, 3]), [2, 4])
        self.assertEqual(list_difference(["1", "2", "3", "4"], ["1", "3"]), ["2", "4"])

        self.assertEqual(list_difference([1, 2, 3, 4], []), [1, 2, 3, 4])
        self.assertEqual(list_difference([], [1, 3]), [])

        self.assertEqual(list_difference([1, 3], [1, 3]), [])

        self.assertEqual(list_difference([2, 4], [1, 3]), [2, 4])


if __name__ == "__main__":
    unittest.main()
