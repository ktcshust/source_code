# mongo async I/O
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

_client = None
_db = None

def get_client():
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
        _db = _client[settings.MONGO_DB]
    return _client, _db

async def insert_summary(summary_doc: dict):
    _, db = get_client()
    # upsert by article_id
    await db.summaries.update_one(
        {"article_id": summary_doc["article_id"]},
        {"$set": summary_doc},
        upsert=True
    )

async def list_summaries(since_ts=None, limit=100):
    _, db = get_client()
    q = {}
    if since_ts:
        q["created_at"] = {"$gte": since_ts}
    cur = db.summaries.find(q).sort("created_at", -1).limit(limit)
    return [doc async for doc in cur]
