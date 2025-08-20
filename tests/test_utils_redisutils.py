import time
import unittest

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

    def test_set_last_user_action(self):
        user_id = int(time.time())

        lasttime_first = self.redisutils.set_last_user_action(user_id, "action")
        self.assertEqual(lasttime_first, 0)

        time.sleep(1)
        lasttime_second = self.redisutils.set_last_user_action(user_id, "action")
        self.assertNotEqual(lasttime_second, 0)

        lasttime_other = self.redisutils.set_last_user_action(user_id, "action2")
        self.assertEqual(lasttime_other, 0)

        time.sleep(2)
        lasttime_third = self.redisutils.set_last_user_action(user_id, "action")
        time_on_third = int(time.time())
        self.assertEqual(lasttime_third - lasttime_second, 1)  # time on second - time on first

        time.sleep(3)
        lasttime_4 = self.redisutils.set_last_user_action(user_id, "action")
        self.assertEqual(lasttime_4, time_on_third)  # time on third get now


if __name__ == "__main__":
    unittest.main()
