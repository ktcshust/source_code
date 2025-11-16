import asyncio
import feedparser
import datetime
from typing import List
from app.config import settings
from app.publishers.message_bus import RedisStreamPublisher, KafkaPublisher
from app.utils.robots import can_fetch

from httpx import AsyncClient

PUBLISHER = None
if settings.PUBLISHER == "redis":
    PUBLISHER = RedisStreamPublisher()
else:
    PUBLISHER = KafkaPublisher()

async def fetch_rss(url: str):
    # check robots
    if not await can_fetch(url, settings.DEFAULT_USER_AGENT):
        return []
    # use feedparser (blocking) in thread to keep simple
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, feedparser.parse, url)
    entries = []
    for e in data.entries:
        entry = {
            "id": e.get("id") or e.get("link"),
            "title": e.get("title"),
            "link": e.get("link"),
            "published": e.get("published", ""),
            "fetched_at": datetime.datetime.utcnow().isoformat(),
            "source": url,
        }
        entries.append(entry)
    return entries

async def publish_entries(entries):
    for e in entries:
        payload = {"type": "article_discovered", "payload": e}
        await PUBLISHER.publish(payload)

async def run_all_feed_sources():
    tasks = [fetch_rss(s) for s in settings.RSS_SOURCES]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in results:
        if isinstance(r, Exception):
            continue
        await publish_entries(r)
