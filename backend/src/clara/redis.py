from redis import Redis
from rq import Queue

from clara.config import get_settings

redis_conn = Redis.from_url(str(get_settings().redis_url))
default_queue = Queue("default", connection=redis_conn)
