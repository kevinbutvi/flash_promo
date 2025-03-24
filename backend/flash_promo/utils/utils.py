from django.conf import settings
import redis

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2, decode_responses=True
)
