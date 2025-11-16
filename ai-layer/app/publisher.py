import redis.asyncio as redis, json
from app.config import settings

_r = redis.from_url(settings.REDIS_URL)

async def publish_for_ai_summary(summary_doc, stream_name=None):
    if not stream_name:
        stream_name = settings.PUBLISH_SUMMARY_STREAM
    await _r.xadd(stream_name, {"data": json.dumps(summary_doc)}, maxlen=20000)
