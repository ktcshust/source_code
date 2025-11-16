# Redis stream consumer -> FilterAgent -> WriterAgent
import asyncio, json
import os
from redis.asyncio import Redis
from app.config import settings
from app.filter_agent import relevance_score
from app.writer_agent import summarize_article
from app.storage import insert_summary
from app.publisher import publish_for_ai_summary  # small helper - we include below

REDIS = Redis.from_url(settings.REDIS_URL)
STREAM = settings.INPUT_STREAM  # default "processing:ingested"
GROUP = "ai-layer-group"
CONSUMER = f"ai-{os.getpid()}"

async def ensure_group():
    try:
        await REDIS.xgroup_create(STREAM, GROUP, id="$", mkstream=True)
    except Exception:
        pass

async def handle_msg(msg_id, fields):
    raw = json.loads(fields.get("data"))
    article = raw.get("article") or raw.get("payload") or raw
    # article expected: dict with article_id, title, link, text
    # step 1: relevance
    rel = await relevance_score(article.get("text",""), article.get("title"))
    if not rel.get("is_relevant", False):
        # skip: optionally publish a small event to indicate skip
        await REDIS.xadd("ai:skipped", {"data": json.dumps({"article_id": article.get("article_id"), "score": rel["relevance_score"]})})
        await REDIS.xack(STREAM, GROUP, msg_id)
        return
    # step 2: summarize
    summary_doc = await summarize_article(article)
    # step 3: store
    await insert_summary(summary_doc)
    # step 4: publish summary for downstream consumers (report generator)
    await publish_for_ai_summary(summary_doc)
    await REDIS.xack(STREAM, GROUP, msg_id)

async def consumer_loop():
    await ensure_group()
    while True:
        res = await REDIS.xreadgroup(GROUP, CONSUMER, streams={STREAM: ">"}, count=5, block=5000)
        if not res:
            await asyncio.sleep(0.5)
            continue
        for stream, messages in res:
            for msg_id, fields in messages:
                try:
                    await handle_msg(msg_id, fields)
                except Exception as e:
                    # push to dlq
                    await REDIS.xadd("ai:dlq", {"data": json.dumps({"msg_id": msg_id, "error": str(e)})})
                    await REDIS.xack(STREAM, GROUP, msg_id)

if __name__ == "__main__":
    asyncio.run(consumer_loop())

