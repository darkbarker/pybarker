import pickle
try:
    import redis
except ImportError as exc:
    raise ImportError("Couldn't import redis-py. Are you sure it's installed?") from exc


class SharedStorage(object):

    IATTR = ("rediscon", "redis_prefix")

    def __init__(self, redis_url, redis_prefix="sharedstorage"):
        self.rediscon = redis.Redis.from_url(url=redis_url)
        self.redis_prefix = redis_prefix

    def _make_key(self, name):
        return "%s:%s" % (self.redis_prefix, name)

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        if name in self.IATTR:
            return super().__setattr__(name, value)
        self.set(name, value)

    def __delattr__(self, name):
        self.delete(name)

    def get(self, name, default=None):
        p_val = self.rediscon.get(self._make_key(name))
        val = pickle.loads(p_val) if p_val is not None else None
        return val if val is not None else default

    def set(self, name, value):
        p_value = pickle.dumps(value, protocol=4)
        self.rediscon.set(name=self._make_key(name), value=p_value)

    def delete(self, name):
        self.rediscon.delete(self._make_key(name))
