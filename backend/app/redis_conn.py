from redis import Redis
from common.config import settings
def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url)
