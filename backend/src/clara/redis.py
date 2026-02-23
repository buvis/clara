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


def blacklist_token(jti: str, ttl_seconds: int) -> None:
    """Add a JWT ID to the blacklist with expiry matching token lifetime."""
    if ttl_seconds > 0:
        get_redis().setex(f"blacklist:{jti}", ttl_seconds, "1")


def is_token_blacklisted(jti: str) -> bool:
    return get_redis().exists(f"blacklist:{jti}") > 0
