import os
import unittest
from time import time, sleep

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.django_test_settings'  # noqa
django.setup()  # noqa

from django.db.models import signals
from django.db.models.query import QuerySet

from pybarker.django.utils import decachetive


class TestCache(unittest.TestCase):

    def setUp(self):
        pass

    def test_one_or_tuple_to_list(self):
        self.assertEqual(decachetive._one_or_tuple_to_list(1), [1])
        self.assertEqual(decachetive._one_or_tuple_to_list([1]), [[1]])
        self.assertEqual(decachetive._one_or_tuple_to_list((1, 2, 3)), [1, 2, 3])
        self.assertEqual(decachetive._one_or_tuple_to_list("test"), ["test"])
        self.assertEqual(decachetive._one_or_tuple_to_list(["test", "test2"]), [["test", "test2"]])
        self.assertEqual(decachetive._one_or_tuple_to_list({"test", "test"}), [{"test"}])

    def test_make_func_id(self):
        def testf():
            pass
        # __main__.TestCache.test__make_func_id.<locals>.testf
        self.assertRegex(decachetive._make_func_id(testf), r"^.+\.TestCache\..+\.testf$")
        # __main__.TestCache.test_make_func_id
        self.assertRegex(decachetive._make_func_id(TestCache.test_make_func_id), r"^.+\.TestCache\.test_make_func_id$")

    def test_make_cache_keys(self):
        self.assertEqual(decachetive._make_cache_keys("keyname", []), ["keyname"])
        self.assertEqual(decachetive._make_cache_keys("keyname", [1]), ["keyname::1"])
        self.assertEqual(decachetive._make_cache_keys("keyname", [1, 2]), ["keyname::1::2"])
        self.assertEqual(decachetive._make_cache_keys("keyname", [1, 2, "3"]), ["keyname::1::2::3"])

        self.assertEqual(decachetive._make_cache_keys("keyname", [1, 2, [3, 4]]), ["keyname::1::2::3", "keyname::1::2::4"])
        self.assertEqual(decachetive._make_cache_keys("keyname", [1, [2, 3], 4]), ["keyname::1::2::4", "keyname::1::3::4"])

        self.assertEqual(decachetive._make_cache_keys("keyname", [1, 2, [3]]), ["keyname::1::2::3"])
        self.assertEqual(decachetive._make_cache_keys("keyname", [1, [2]]), ["keyname::1::2"])
        self.assertEqual(decachetive._make_cache_keys("keyname", [[1, 2]]), ["keyname::1", "keyname::2"])
        # sic! вообще не должно сгенериться ключей, ибо у нас формат ключей "keyname::1::ххх", а генерить не из чего
        self.assertEqual(decachetive._make_cache_keys("keyname", [1, []]), [])

        with self.assertRaises(ValueError):  # "LISTEDSUFFIX must be once"
            decachetive._make_cache_keys("keyname", [1, [2, 3], [4]])

        self.assertEqual(decachetive._make_cache_keys("keyname", [1, None]), ["keyname::1::None"])
        self.assertEqual(decachetive._make_cache_keys("keyname", [None]), ["keyname::None"])
        self.assertEqual(decachetive._make_cache_keys("keyname", [1, [2, None]]), ["keyname::1::2", "keyname::1::None"])

    def test_timeout(self):

        @decachetive.decachetived(timeout=1)
        def _do_timeout():
            return time()

        val1 = _do_timeout()
        sleep(0.1)
        val2 = _do_timeout()
        sleep(1.4)
        val3 = _do_timeout()
        self.assertEqual(val1, val2)
        self.assertNotEqual(val1, val3)
        self.assertNotEqual(val2, val3)

    def test_keyname(self):

        @decachetive.decachetived(timeout=1, keyname="testkeyname")
        def _do_timeout(n):
            return time() + n

        val1 = _do_timeout(1)
        sleep(0.1)
        val2 = _do_timeout(1)
        sleep(1.4)
        val3 = _do_timeout(1)
        self.assertEqual(val1, val2)
        self.assertNotEqual(val1, val3)
        self.assertNotEqual(val2, val3)

    def test_suffix(self):

        @decachetive.decachetived(timeout=1, suffix=lambda n: n,)
        def _do_timeout(n):
            return time() + n

        val1_1 = _do_timeout(1)
        val2_1 = _do_timeout(2)
        val3_1 = _do_timeout(1)

        self.assertEqual(val1_1, val3_1)
        self.assertNotEqual(val1_1, val2_1)
        self.assertNotEqual(val3_1, val2_1)

        val1_2 = _do_timeout(1)
        val2_2 = _do_timeout(2)
        val3_2 = _do_timeout(1)

        self.assertEqual(val1_1, val1_2)
        self.assertEqual(val2_1, val2_2)
        self.assertEqual(val3_1, val3_2)

        sleep(1.5)

        val1_3 = _do_timeout(1)
        val2_3 = _do_timeout(2)
        val3_3 = _do_timeout(1)

        self.assertNotEqual(val1_2, val1_3)
        self.assertNotEqual(val2_2, val2_3)
        self.assertNotEqual(val3_2, val3_3)

        self.assertEqual(val1_3, val3_3)
        self.assertNotEqual(val1_3, val2_3)

    def _test_pugre_function_or_keyname(self, _do_timeout, cached_function_or_keyname):

        val1_1 = _do_timeout(1)
        val2_1 = _do_timeout(2)
        val3_1 = _do_timeout(1)

        self.assertEqual(val1_1, val3_1)
        self.assertNotEqual(val1_1, val2_1)
        self.assertNotEqual(val3_1, val2_1)

        decachetive.purge_cache(cached_function_or_keyname, 3)
        decachetive.purge_cache(cached_function_or_keyname, 3, 1)
        decachetive.purge_cache(cached_function_or_keyname)
        decachetive.purge_cache(cached_function_or_keyname, None)

        val1_2 = _do_timeout(1)
        val2_2 = _do_timeout(2)
        val3_2 = _do_timeout(1)

        self.assertEqual(val1_1, val1_2)
        self.assertEqual(val2_1, val2_2)
        self.assertEqual(val3_1, val3_2)

        decachetive.purge_cache(cached_function_or_keyname, 1)

        val1_3 = _do_timeout(1)
        val2_3 = _do_timeout(2)
        val3_3 = _do_timeout(1)

        self.assertNotEqual(val1_2, val1_3)
        self.assertEqual(val2_2, val2_3)
        self.assertNotEqual(val3_2, val3_3)

        self.assertEqual(val1_3, val3_3)

        decachetive.purge_cache(cached_function_or_keyname, 2)

        val1_4 = _do_timeout(1)
        val2_4 = _do_timeout(2)
        val3_4 = _do_timeout(1)

        self.assertEqual(val1_3, val1_4)
        self.assertNotEqual(val2_3, val2_4)
        self.assertEqual(val3_3, val3_4)

        # мультикей списком
        val1_5 = _do_timeout(1)
        val2_5 = _do_timeout(2)
        val3_5 = _do_timeout(1)

        self.assertEqual(val1_4, val1_5)
        self.assertEqual(val2_4, val2_5)
        self.assertEqual(val3_4, val3_5)

        decachetive.purge_cache(cached_function_or_keyname, 3)
        decachetive.purge_cache(cached_function_or_keyname, 1, [])
        decachetive.purge_cache(cached_function_or_keyname, [], 2)

        val1_6 = _do_timeout(1)
        val2_6 = _do_timeout(2)
        val3_6 = _do_timeout(1)

        self.assertEqual(val1_5, val1_6)
        self.assertEqual(val2_5, val2_6)
        self.assertEqual(val3_5, val3_6)

        decachetive.purge_cache(cached_function_or_keyname, [2, 3, 5])

        val1_7 = _do_timeout(1)
        val2_7 = _do_timeout(2)
        val3_7 = _do_timeout(1)

        self.assertEqual(val1_6, val1_7)
        self.assertNotEqual(val2_6, val2_7)
        self.assertEqual(val3_6, val3_7)

    def test_purge_function(self):

        @decachetive.decachetived(timeout=1, suffix=lambda n: n,)
        def _do_timeout(n):
            return time() + n

        self._test_pugre_function_or_keyname(_do_timeout, _do_timeout)

    def test_purge_keyname(self):

        @decachetive.decachetived(timeout=1, keyname="testkeyname", suffix=lambda n: n,)
        def _do_timeout(n):
            return time() + n

        self._test_pugre_function_or_keyname(_do_timeout, "testkeyname")

    def test_check_depends(self):
        class Model1:
            pk1 = None

        class Model2:
            pk2 = None

        lambda1 = lambda m1: m1.pk1  # noqa

        depend = [(Model1, lambda1), (Model2,)]
        self.assertEqual(decachetive._check_depends(depend), [(Model1, lambda1), (Model2, None)])
        depend = [("model.Model1", lambda1), ("model.Model2",)]
        self.assertEqual(decachetive._check_depends(depend), [("model.Model1", lambda1), ("model.Model2", None)])

        depend = [(Model1,), Model2]
        self.assertEqual(decachetive._check_depends(depend), [(Model1, None), (Model2, None)])
        depend = [("model.Model1",), "model.Model2"]
        self.assertEqual(decachetive._check_depends(depend), [("model.Model1", None), ("model.Model2", None)])

        depend = (Model1, lambda1)
        self.assertEqual(decachetive._check_depends(depend), [(Model1, lambda1)])
        depend = ("model.Model1", lambda1)
        self.assertEqual(decachetive._check_depends(depend), [("model.Model1", lambda1)])

        depend = (Model1,)
        self.assertEqual(decachetive._check_depends(depend), [(Model1, None)])
        depend = ("model.Model1",)
        self.assertEqual(decachetive._check_depends(depend), [("model.Model1", None)])

        depend = Model1
        self.assertEqual(decachetive._check_depends(depend), [(Model1, None)])
        depend = "model.Model1"
        self.assertEqual(decachetive._check_depends(depend), [("model.Model1", None)])

        depend = [("model.Model1", lambda1),
                  ("model.Model2",),
                  "model.Model3"]
        self.assertEqual(decachetive._check_depends(depend), [("model.Model1", lambda1), ("model.Model2", None), ("model.Model3", None)])

        with self.assertRaises(TypeError) as e:
            decachetive._check_depends([(None, None)])
        self.assertIn("not class-or-str arg-1", str(e.exception))

        with self.assertRaises(TypeError) as e:
            decachetive._check_depends([("model.Model1", "notcallable")])
        self.assertIn("not callable arg-2", str(e.exception))

        with self.assertRaises(TypeError) as e:
            decachetive._check_depends([()])
        self.assertIn("wrong depend tuple-format", str(e.exception))

        with self.assertRaises(TypeError) as e:
            decachetive._check_depends([("model.Model1", None, "third")])
        self.assertIn("wrong depend tuple-format", str(e.exception))

    # проверки на проверку валидности сигнатур итд
    def test_check_depends_2(self):

        class Model1:
            pk1 = None

        # сигнатура лямбды - один параметр (инстанс)

        @decachetive.decachetived(
            timeout=1,
            suffix=lambda n: n,
            depend=[(Model1, lambda m1: m1.pk1)],
        )
        def _normal_1(n):
            return time() + n

        with self.assertRaises(TypeError) as e:
            @decachetive.decachetived(
                timeout=1,
                suffix=lambda n: n,
                depend=[(Model1, lambda m1, m11: m1.pk1)],
            )
            def _error_2_param(n):
                return time() + n
        self.assertIn("wrong depend format", str(e.exception))
        self.assertIn("not one-param, but 2", str(e.exception))

        with self.assertRaises(TypeError) as e:
            @decachetive.decachetived(
                timeout=1,
                suffix=lambda n: n,
                depend=[(Model1, lambda: 666)],
            )
            def _error_0_param(n):
                return time() + n
        self.assertIn("wrong depend format", str(e.exception))
        self.assertIn("not one-param, but 0", str(e.exception))

    def test_depend(self):

        class Model1:
            pk1 = None

            def __repr__(self):
                return "model1 #%s" % self.pk1

        class Model2:
            pk2 = None

            def __repr__(self):
                return "model2 #%s" % self.pk2

        @decachetive.decachetived(
            timeout=1,
            suffix=lambda n: n,
            depend=[(Model1, lambda m1: m1.pk1),
                    (Model2, lambda m2: m2.pk2)],
            debug=False,
        )
        def _do_timeout(n):
            return time() + n

        val1_1 = _do_timeout(1)
        val2_1 = _do_timeout(2)
        val3_1 = _do_timeout(1)

        self.assertEqual(val1_1, val3_1)
        self.assertNotEqual(val1_1, val2_1)
        self.assertNotEqual(val3_1, val2_1)

        m3 = Model1()
        m3.pk1 = 3

        signals.post_save.send(sender=Model1, instance=m3)
        signals.post_delete.send(sender=Model1, instance=m3)

        m4 = Model2()
        m4.pk2 = 4

        signals.post_save.send(sender=Model2, instance=m4)
        signals.post_delete.send(sender=Model2, instance=m4)

        val1_2 = _do_timeout(1)
        val2_2 = _do_timeout(2)
        val3_2 = _do_timeout(1)

        self.assertEqual(val1_1, val1_2)
        self.assertEqual(val2_1, val2_2)
        self.assertEqual(val3_1, val3_2)

        m1 = Model1()
        m1.pk1 = 1

        signals.post_save.send(sender=Model1, instance=m1)

        val1_3 = _do_timeout(1)
        val2_3 = _do_timeout(2)
        val3_3 = _do_timeout(1)

        self.assertNotEqual(val1_2, val1_3)
        self.assertEqual(val2_2, val2_3)
        self.assertNotEqual(val3_2, val3_3)

        self.assertEqual(val1_3, val3_3)

        m2 = Model1()  # sic
        m2.pk1 = 2

        signals.post_delete.send(sender=Model1, instance=m2)

        val1_4 = _do_timeout(1)
        val2_4 = _do_timeout(2)
        val3_4 = _do_timeout(1)

        self.assertEqual(val1_3, val1_4)
        self.assertNotEqual(val2_3, val2_4)
        self.assertEqual(val3_3, val3_4)

        m1 = Model2()
        m1.pk2 = 1  # sic

        signals.post_delete.send(sender=Model2, instance=m1)

        val1_5 = _do_timeout(1)
        val2_5 = _do_timeout(2)
        val3_5 = _do_timeout(1)

        self.assertNotEqual(val1_4, val1_5)
        self.assertEqual(val2_4, val2_5)
        self.assertNotEqual(val3_4, val3_5)

    # с ключами длины 2
    def test_depend_2(self):
        class Model3:
            p1 = None
            p2 = None

            def __repr__(self):
                return "model3 #%s #%s" % (self.p1, self.p2)

        class Model4:
            p1 = None
            p2 = None

        @decachetive.decachetived(
            timeout=1,
            suffix=lambda n, p: (n, p),
            depend=[(Model3, lambda m3: (m3.p1, m3.p2))],
            debug=False,
        )
        def _do_timeout(n, p):
            return time() + n * p

        val1_1 = _do_timeout(1, 2)
        val2_1 = _do_timeout(2, 5)
        val3_1 = _do_timeout(1, 2)

        self.assertEqual(val1_1, val3_1)
        self.assertNotEqual(val1_1, val2_1)
        self.assertNotEqual(val3_1, val2_1)

        m3 = Model3()
        m3.p1 = 3
        m3.p2 = 4
        signals.post_save.send(sender=Model3, instance=m3)

        val1_2 = _do_timeout(1, 2)
        val2_2 = _do_timeout(2, 5)
        val3_2 = _do_timeout(1, 2)

        self.assertEqual(val1_1, val1_2)
        self.assertEqual(val2_1, val2_2)
        self.assertEqual(val3_1, val3_2)

        m3 = Model3()
        m3.p1 = 1
        m3.p2 = 2
        signals.post_save.send(sender=Model3, instance=m3)

        val1_3 = _do_timeout(1, 2)
        val2_3 = _do_timeout(2, 5)
        val3_3 = _do_timeout(1, 2)

        self.assertNotEqual(val1_2, val1_3)
        self.assertEqual(val2_2, val2_3)
        self.assertNotEqual(val3_2, val3_3)

        self.assertEqual(val1_3, val3_3)

        m3 = Model3()
        m3.p1 = 2
        m3.p2 = 5
        signals.post_delete.send(sender=Model3, instance=m3)

        val1_4 = _do_timeout(1, 2)
        val2_4 = _do_timeout(2, 5)
        val3_4 = _do_timeout(1, 2)

        self.assertEqual(val1_3, val1_4)
        self.assertNotEqual(val2_3, val2_4)
        self.assertEqual(val3_3, val3_4)

        m3 = Model3()
        m3.p1 = 1
        m3.p2 = 2
        signals.post_delete.send(sender=Model3, instance=m3)

        val1_5 = _do_timeout(1, 2)
        val2_5 = _do_timeout(2, 5)
        val3_5 = _do_timeout(1, 2)

        self.assertNotEqual(val1_4, val1_5)
        self.assertEqual(val2_4, val2_5)
        self.assertNotEqual(val3_4, val3_5)

        # novalid match
        m3 = Model3()
        m3.p1 = 1
        m3.p2 = 3
        signals.post_delete.send(sender=Model3, instance=m3)

        m3 = Model3()
        m3.p1 = 2
        m3.p2 = 2
        signals.post_delete.send(sender=Model3, instance=m3)

        m4 = Model4()
        m4.p1 = 1
        m4.p2 = 2
        signals.post_delete.send(sender=Model4, instance=m4)

        m4 = Model4()
        m4.p1 = 2
        m4.p2 = 5
        signals.post_delete.send(sender=Model4, instance=m4)

        val1_6 = _do_timeout(1, 2)
        val2_6 = _do_timeout(2, 5)
        val3_6 = _do_timeout(1, 2)

        self.assertEqual(val1_5, val1_6)
        self.assertEqual(val2_5, val2_6)
        self.assertEqual(val3_5, val3_6)

        # valid match
        m3 = Model3()
        m3.p1 = 1
        m3.p2 = 2
        signals.post_delete.send(sender=Model3, instance=m3)

        val1_7 = _do_timeout(1, 2)
        val2_7 = _do_timeout(2, 5)
        val3_7 = _do_timeout(1, 2)

        self.assertNotEqual(val1_6, val1_7)
        self.assertEqual(val2_6, val2_7)
        self.assertNotEqual(val3_6, val3_7)

    # один аргумент и только один массив (проверка то он не свернётся в один список суффиксов)
    def test_multikeys_array1(self):
        class Model1:
            p1 = None

        @decachetive.decachetived(
            timeout=1,
            suffix=lambda n: n,
            depend=[(Model1, lambda _: ([1, 3]))],
            debug=False
        )
        def _do_timeout_array1(n):
            return time() + n

        val1_1 = _do_timeout_array1(1)
        val2_1 = _do_timeout_array1(2)
        val3_1 = _do_timeout_array1(1)

        self.assertEqual(val1_1, val3_1)
        self.assertNotEqual(val1_1, val2_1)
        self.assertNotEqual(val3_1, val2_1)

        m1 = Model1()
        signals.post_save.send(sender=Model1, instance=m1)

        val1_2 = _do_timeout_array1(1)
        val2_2 = _do_timeout_array1(2)
        val3_2 = _do_timeout_array1(1)

        self.assertNotEqual(val1_1, val1_2)
        self.assertEqual(val2_1, val2_2)
        self.assertNotEqual(val3_1, val3_2)

    # два аргумента, с массивом
    def test_multikeys_array2(self):
        class Model1:
            p1 = None

        @decachetive.decachetived(
            timeout=1,
            suffix=lambda n, p: (n, p),
            depend=[(Model1, lambda m3: (m3.p1, [1, 2, 3]))],
            debug=False,
        )
        def _do_timeout_array2(n, p):
            return time() + n * p

        val1_1 = _do_timeout_array2(1, 2)
        val2_1 = _do_timeout_array2(2, 5)
        val3_1 = _do_timeout_array2(1, 2)

        self.assertEqual(val1_1, val3_1)
        self.assertNotEqual(val1_1, val2_1)
        self.assertNotEqual(val3_1, val2_1)

        # не сброс 3 + [1, 2, 3]
        m1 = Model1()
        m1.p1 = 3
        signals.post_save.send(sender=Model1, instance=m1)

        val1_2 = _do_timeout_array2(1, 2)
        val2_2 = _do_timeout_array2(2, 5)
        val3_2 = _do_timeout_array2(1, 2)

        self.assertEqual(val1_1, val1_2)
        self.assertEqual(val2_1, val2_2)
        self.assertEqual(val3_1, val3_2)

        # сброс 1 + [1, 2, 3]
        m1 = Model1()
        m1.p1 = 1
        signals.post_save.send(sender=Model1, instance=m1)

        val1_3 = _do_timeout_array2(1, 2)
        val2_3 = _do_timeout_array2(2, 5)
        val3_3 = _do_timeout_array2(1, 2)

        self.assertNotEqual(val1_2, val1_3)
        self.assertEqual(val2_2, val2_3)
        self.assertNotEqual(val3_2, val3_3)

    # вместо массива вызов функции
    def test_multikeys_func(self):

        def func_array():
            return [1, 3]

        class Model1:
            p1 = None

        @decachetive.decachetived(
            timeout=1,
            suffix=lambda n: n,
            depend=[(Model1, lambda _: (func_array()))],
            debug=False
        )
        def _do_timeout_array_func(n):
            return time() + n

        val1_1 = _do_timeout_array_func(1)
        val2_1 = _do_timeout_array_func(2)
        val3_1 = _do_timeout_array_func(1)

        self.assertEqual(val1_1, val3_1)
        self.assertNotEqual(val1_1, val2_1)
        self.assertNotEqual(val3_1, val2_1)

        m1 = Model1()
        signals.post_save.send(sender=Model1, instance=m1)
        signals.post_save.send(sender=Model1, instance=m1)
        signals.post_save.send(sender=Model1, instance=m1)

        val1_2 = _do_timeout_array_func(1)
        val2_2 = _do_timeout_array_func(2)
        val3_2 = _do_timeout_array_func(1)

        self.assertNotEqual(val1_1, val1_2)
        self.assertEqual(val2_1, val2_2)
        self.assertNotEqual(val3_1, val3_2)

    # ошибка кеширования кверисета должна быть
    def test_fail_queryset(self):

        @decachetive.decachetived(
            timeout=1,
        )
        def _get_queryset():
            return QuerySet()

        # дважды подряд чтобы убедиться что и не кешируется и ругается ДО
        with self.assertRaises(Exception) as e:
            _get_queryset()
        self.assertIn("incorrectly", str(e.exception))
        with self.assertRaises(Exception) as e:
            _get_queryset()
        self.assertIn("incorrectly", str(e.exception))


if __name__ == "__main__":
    unittest.main()
