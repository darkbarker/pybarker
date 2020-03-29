import random
import time
try:
    import redis
except ImportError as exc:
    raise ImportError("Couldn't import redis-py. Are you sure it's installed?") from exc


class OtpStore(object):

    def __init__(self, redis_url, timeout=300, otp_length=4, retry_timeout=60, redis_prefix="otp"):
        self.rediscon = redis.Redis.from_url(url=redis_url)
        self.timeout = timeout
        self.otp_length = otp_length
        self.retry_timeout = retry_timeout
        self.redis_prefix = redis_prefix

    def _make_key(self, user_id):
        return "%s:%s" % (self.redis_prefix, user_id)

    def generate_otp(self):
        range_start = 10**(self.otp_length - 1)
        range_end = (10**self.otp_length) - 1
        return str(random.randint(range_start, range_end))

    def set(self, user_id, pwd):
        self.rediscon.setex(name=self._make_key(user_id), value=pwd, time=self.timeout)

    def get(self, user_id):
        val = self.rediscon.get(self._make_key(user_id))  # get bytes
        return val.decode("latin1") if val is not None else None

    def _make_retry_key(self, entity_id):
        return "%s:r:%s" % (self.redis_prefix, entity_id)

    # reset the send timeout, remember when it was sent
    def reset_retry_timeout(self, entity_id):
        time_now = int(time.time())
        self.rediscon.setex(name=self._make_retry_key(entity_id), value=time_now, time=self.retry_timeout)

    # receiving number of seconds remaining to sending, 0 - already possible
    # entity_id - e.g. user_id or request ip
    def get_retry_time(self, entity_id):
        time_now = int(time.time())
        time_last = int(self.rediscon.get(self._make_retry_key(entity_id)) or 0)
        retry_time = time_last + self.retry_timeout - time_now
        return retry_time if retry_time > 0 else 0
