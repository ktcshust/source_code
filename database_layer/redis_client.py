# aioredis client# redis_client.py
from redis import Redis
from .db_config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

