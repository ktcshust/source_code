# publish to next topic/stream
import os, json
from app.schemas import ProcessingJob
from typing import Dict, Any
from app.config import settings

# reuse same publisher as in input-layer; minimal Redis Streams publisher
import redis.asyncio as redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_stream = None

async def get_redis():
    global _stream
    if _stream is None:
        _stream = redis.from_url(REDIS_URL)
    return _stream

async def publish_for_ai(job: Dict[str, Any], stream_name="processing:ingested"):
    r = await get_redis()
    # message fields are strings -> json-serialize
    await r.xadd(stream_name, {"data": json.dumps(job)}, maxlen=10000)
