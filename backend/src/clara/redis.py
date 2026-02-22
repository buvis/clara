from redis import Redis
from rq import Queue

from clara.config import get_settings

_redis: Redis | None = None
_queue: Queue | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(str(get_settings().redis_url))
    return _redis


def get_queue() -> Queue:
    global _queue
    if _queue is None:
        _queue = Queue("default", connection=get_redis())
    return _queue
