import redis
from django.conf import settings

# Redis client for counters
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

def increment_failed_login(user_id):
    key = f"failed_login:{user_id}"
    count = redis_client.incr(key)
    redis_client.expire(key, 3600)  # expire after 1 hour
    return count

def reset_failed_login(user_id):
    key = f"failed_login:{user_id}"
    redis_client.delete(key)
    
