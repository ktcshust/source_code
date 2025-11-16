import asyncio
from app.utils.robots import can_fetch
from app.utils.html_text import extract_text
from app.config import settings
from app.publishers.message_bus import RedisStreamPublisher, KafkaPublisher
from httpx import AsyncClient

PUBLISHER = None
if settings.PUBLISHER == "redis":
    PUBLISHER = RedisStreamPublisher()
else:
    PUBLISHER = KafkaPublisher()

async def fetch_page(url: str, timeout=15):
    if not await can_fetch(url, settings.DEFAULT_USER_AGENT):
        raise RuntimeError("disallowed by robots")
    async with AsyncClient(timeout=timeout, headers={"User-Agent": settings.DEFAULT_USER_AGENT}) as client:
        r = await client.get(url)
        r.raise_for_status()
        text = extract_text(r.text)
        return {"url": url, "status": r.status_code, "text": text, "fetched_at": __import__("datetime").datetime.utcnow().isoformat()}

async def fetch_and_publish(url: str):
    doc = await fetch_page(url)
    payload = {"type": "article_html_fetched", "payload": doc}
    await PUBLISHER.publish(payload)
    return doc
