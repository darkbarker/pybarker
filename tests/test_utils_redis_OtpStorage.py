import time
import unittest

from pybarker.utils.otp import OtpStore


class Test(unittest.TestCase):

    APP_REDIS_CONNECTION = "redis://localhost:6379/3"
    OTP_PASS_TIMEOUT = 5
    OTP_PASS_LENGTH = 6
    OTP_RETRY_TIMEOUT = 7

    def setUp(self):

        self.otp_store = OtpStore(
            self.APP_REDIS_CONNECTION,
            timeout=self.OTP_PASS_TIMEOUT,
            otp_length=self.OTP_PASS_LENGTH,
            retry_timeout=self.OTP_RETRY_TIMEOUT,
        )

    def test_retry_timeout(self):
        user_id = int(time.time() * 1000)

        self.assertEqual(self.otp_store.get_retry_time(user_id), 0)

        self.assertEqual(self.otp_store.retry_timeout, self.OTP_RETRY_TIMEOUT)

        self.otp_store.reset_retry_timeout(user_id)

        self.assertEqual(self.otp_store.get_retry_time(user_id), self.OTP_RETRY_TIMEOUT)

        h = self.OTP_RETRY_TIMEOUT // 2  # 5
        time.sleep(h)

        self.assertEqual(self.otp_store.get_retry_time(user_id), (self.OTP_RETRY_TIMEOUT - h))  # остаток=10-5

        time.sleep(self.OTP_RETRY_TIMEOUT - h + 1)  # остаток + 1

        self.assertEqual(self.otp_store.get_retry_time(user_id), 0)

    def test_otp_length(self):

        self.assertEqual(self.otp_store.otp_length, self.OTP_PASS_LENGTH)

        self.assertIsInstance(self.otp_store.generate_otp(), str)

        for _ in range(100):
            self.assertEqual(len(str(self.otp_store.generate_otp())), self.OTP_PASS_LENGTH)

    def test_timeout(self):
        user_id = int(time.time() * 1000)

        self.assertEqual(self.otp_store.get(user_id), None)

        self.assertEqual(self.otp_store.timeout, self.OTP_PASS_TIMEOUT)

        otp = self.otp_store.generate_otp()
        self.assertIsInstance(otp, str)

        self.otp_store.set(user_id, otp)

        self.assertEqual(self.otp_store.get(user_id), otp)
        self.assertIsInstance(self.otp_store.get(user_id), str)

        time.sleep(1)

        self.assertEqual(self.otp_store.get(user_id), otp)
        self.assertIsInstance(self.otp_store.get(user_id), str)

        time.sleep(self.OTP_PASS_TIMEOUT)

        self.assertEqual(self.otp_store.get(user_id), None)

        # int
        self.otp_store.set(user_id, 666)
        self.assertEqual(self.otp_store.get(user_id), "666")
        time.sleep(self.OTP_PASS_TIMEOUT + 1)
        self.assertEqual(self.otp_store.get(user_id), None)


if __name__ == "__main__":
    unittest.main()
