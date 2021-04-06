import unittest
import time

from pybarker.utils.redis import SharedStorage


class Test(unittest.TestCase):

    APP_REDIS_CONNECTION = 'redis://localhost:6379/3'

    def setUp(self):

        self.shared_storage = SharedStorage(
            self.APP_REDIS_CONNECTION,
        )
        self.shared_storage2 = SharedStorage(
            self.APP_REDIS_CONNECTION,
        )

    def test_retry_timeout(self):
        valint = int(time.time() * 1000)
        valstr = str(valint)
        valobj = {"str": valstr, "int": valint}
        print("valobj:", valobj)

        self.shared_storage.BEN = valstr
        self.assertEqual(self.shared_storage.BEN, valstr)

        self.shared_storage.BEN = valint
        self.assertEqual(self.shared_storage.BEN, valint)

        self.shared_storage.BEN = valobj
        self.assertEqual(self.shared_storage.BEN, valobj)

        self.shared_storage.BEN = None
        self.assertEqual(self.shared_storage.BEN, None)

        # other instance storage
        self.assertEqual(self.shared_storage2.BEN, None)
        self.shared_storage.BEN = valstr
        self.assertEqual(self.shared_storage2.BEN, valstr)
        self.shared_storage.BEN = valint
        self.assertEqual(self.shared_storage2.BEN, valint)
        self.shared_storage.BEN = valobj
        self.assertEqual(self.shared_storage2.BEN, valobj)
        self.shared_storage.BEN = None
        self.assertEqual(self.shared_storage2.BEN, None)

        # missing
        self.assertEqual(self.shared_storage.BEN666, None)

        # set, get
        self.shared_storage.set("BEN", valint)
        self.assertEqual(self.shared_storage.get("BEN"), valint)
        self.assertEqual(self.shared_storage.get("BEN666"), None)
        self.assertEqual(self.shared_storage.get("BEN666", 666), 666)
        self.shared_storage.set("BEN", valobj)
        self.assertEqual(self.shared_storage.get("BEN"), valobj)

        # del
        self.shared_storage.BEN = valstr
        self.assertEqual(self.shared_storage.BEN, valstr)
        del self.shared_storage.BEN
        self.assertEqual(self.shared_storage.BEN, None)
        # del + other instance storage
        self.assertEqual(self.shared_storage2.BEN, None)
        self.shared_storage.BEN = valstr
        self.assertEqual(self.shared_storage2.BEN, valstr)
        self.shared_storage.delete("BEN")
        self.assertEqual(self.shared_storage2.BEN, None)
        # del silent
        del self.shared_storage.BEN666
        self.shared_storage.delete("BEN666")


if __name__ == '__main__':
    unittest.main()
