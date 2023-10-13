import pickle
import time

try:
    import redis
except ImportError as exc:
    raise ImportError("Couldn't import redis-py. Are you sure it's installed?") from exc


class RedisUtils(object):

    def __init__(self, redis_url, redis_prefix="redisutils"):
        self.rediscon = redis.Redis.from_url(url=redis_url)
        self.redis_prefix = redis_prefix

    def _make_key(self, name):
        return "%s:%s" % (self.redis_prefix, name)

    # Возвращает время (unixtime) предыдущего обращения (и запоминает новое обращение)
    # к методу, для юзера + какого-то действия, если не было то вернётся 0.
    # может использоваться для вычисления времени для "чего-то с последнего обращения"
    def set_last_user_action(self, user_id: str, action: str, timeout: int=60 * 60 * 24 * 365) -> int:
        key = self._make_key(f"lua_{user_id}_{action}")
        r = int(self.rediscon.get(key) or 0)
        self.rediscon.setex(name=key, value=int(time.time()), time=timeout)
        return r

    # только Возвращает время (unixtime) предыдущего обращения, если не было то вернётся 0.
    def get_last_user_action(self, user_id: str, action: str) -> int:
        key = self._make_key(f"lua_{user_id}_{action}")
        return int(self.rediscon.get(key) or 0)

    # кладёт объект в хранилище, или удаляет если передано None
    # timeout - таймаут в секундах, по умолчанию - год
    def object_to_redis(self, key, val, timeout=60 * 60 * 24 * 365):
        key = self._make_key(f"or_{key}")
        if val is not None:
            p_val = pickle.dumps(val, protocol=4)
            self.rediscon.setex(name=key, value=p_val, time=timeout)
        else:
            self.rediscon.delete(key)

    # получает объект из хранилища, или None если его нет
    def object_from_redis(self, key):
        key = self._make_key(f"or_{key}")
        p_val = self.rediscon.get(key)
        return pickle.loads(p_val) if p_val is not None else None

    # некая строка с кратким статусом или будет экзепшен с ошибкой коннекта например
    def redis_status(self):
        return "dbsize: %s, used mem: %s, ping: %s" % (self.rediscon.dbsize(), self.rediscon.info()["used_memory_human"], self.rediscon.echo("PONG"))

    # кладёт по ключу какому-то счётчик, указывается таймаут, чтобы потом посчитать сколько за это время добавлялось там объектов
    # например количество соединений вебсокета за последние 60 секунд посчитать - каждое содидение кладёт протухающий счётчик итд

    # удаление устаревших, ранее указанного времени
    def _counter_trunc_expired(self, key, time_expired):
        self.rediscon.zremrangebyscore(key, 0, time_expired)

    def redis_inc_counter(self, key, timeout):
        key = self._make_key(f"ic_{key}")
        time_now = time.time()
        self.rediscon.zadd(key, mapping={time_now: time_now})  # добавляются вида: (b'1552659631.0757813', 1552659631.0757813)
        self.rediscon.expire(key, 3600)  # сама очередь тоже протухает чтобы не осталась навечно потом
        self._counter_trunc_expired(key, time_now - timeout)  # здесь тоже удаляем после добавления, вдруг мы не будем вызывать redis_get_counter и накопится дофига

    def redis_get_counter(self, key, timeout):
        key = self._make_key(f"ic_{key}")
        self._counter_trunc_expired(key, time.time() - timeout)
        return self.rediscon.zcount(key, 0, "+inf")
