# Redis Streams consumer + DLQ logic
import asyncio, os, json, time
from redis.asyncio import Redis
from app.db import DB
from app.schemas import ArticleDiscovered, ProcessingJob
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from app.publisher import publish_for_ai
from app.temporal_workflow import start_process_workflow

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
INPUT_STREAM = os.getenv("INPUT_STREAM", "input:articles")
GROUP = os.getenv("CONSUMER_GROUP", "processing-group")
CONSUMER_NAME = os.getenv("CONSUMER_NAME", f"proc-{os.getpid()}")

r = Redis.from_url(REDIS_URL)

async def ensure_group():
    try:
        await r.xgroup_create(INPUT_STREAM, GROUP, id="$", mkstream=True)
    except Exception:
        # group may already exist
        pass

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def ack_message(msg_id: str):
    await r.xack(INPUT_STREAM, GROUP, msg_id)

async def handle_message(msg_id: str, fields: dict):
    """
    fields: {'data': '{"type":"article_discovered", "payload":{...}}' }
    """
    raw = json.loads(fields.get("data"))
    payload = raw.get("payload") or {}
    article = ArticleDiscovered(**payload)
    article_id = article.id or article.link

    # dedup check
    if await DB.is_processed(article_id):
        # already handled: ack and skip
        await ack_message(msg_id)
        return

    # Option A: start a Temporal workflow to handle processing pipeline
    # We wrap with retry to handle transient Temporal errors
    try:
        wf_id = await start_process_workflow(article.dict())
    except Exception as e:
        # If we can't start workflow, push to DLQ stream
        await r.xadd("processing:dlq", {"data": json.dumps({"msg_id": msg_id, "payload": payload, "error": str(e)})})
        return

    # Mark processed optimistically (or can be after workflow success)
    await DB.mark_processed(article_id, article.link, article.title or "")
    # ack the message on the input stream
    await ack_message(msg_id)

async def consumer_loop(poll_interval=1.0):
    await DB.init()
    await ensure_group()
    while True:
        try:
            res = await r.xreadgroup(GROUP, CONSUMER_NAME, streams={INPUT_STREAM: ">"}, count=10, block=5000)
            if not res:
                await asyncio.sleep(poll_interval)
                continue
            # res: list of (stream, [(id, {fields})])
            for stream, messages in res:
                for msg_id, fields in messages:
                    try:
                        await handle_message(msg_id, fields)
                    except Exception as e:
                        # push to DLQ
                        await r.xadd("processing:dlq", {"data": json.dumps({"msg_id": msg_id, "error": str(e)})})
        except Exception as exc:
            # log & sleep a bit
            print("Consumer loop error:", exc)
            await asyncio.sleep(5)

