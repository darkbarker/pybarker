import unittest
import time

from pybarker.utils.redisutils import RedisUtils


class Test(unittest.TestCase):

    APP_REDIS_CONNECTION = "redis://localhost:6379/3"

    def setUp(self):
        self.redisutils = RedisUtils(
            redis_url=self.APP_REDIS_CONNECTION,
            redis_prefix="unittest",
        )

    def test_counter(self):
        key = str(time.time())

        self.assertEqual(self.redisutils.redis_get_counter(key, timeout=5), 0)

        self.redisutils.redis_inc_counter(key, timeout=5)  # +1

        self.assertEqual(self.redisutils.redis_get_counter(key, timeout=5), 1)

        self.redisutils.redis_inc_counter(key, timeout=5)  # +1
        self.redisutils.redis_inc_counter(key, timeout=5)  # +1

        self.assertEqual(self.redisutils.redis_get_counter(key, timeout=5), 3)

        time.sleep(2.5)  # 3-0

        self.assertEqual(self.redisutils.redis_get_counter(key, timeout=5), 3)

        self.redisutils.redis_inc_counter(key, timeout=5)  # +1
        self.redisutils.redis_inc_counter(key, timeout=5)  # +1

        time.sleep(3.5)  # 5-3

        self.assertEqual(self.redisutils.redis_get_counter(key, timeout=5), 2)

        time.sleep(2.5)  # 2-2

        self.assertEqual(self.redisutils.redis_get_counter(key, timeout=5), 0)


if __name__ == "__main__":
    unittest.main()
