# asyncpg helpers, migration helper
import asyncio
import os
import asyncpg
from typing import Optional

DSN = os.getenv("PROCESSING_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

class DB:
    _pool: Optional[asyncpg.pool.Pool] = None

    @classmethod
    async def init(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(dsn=DSN, min_size=1, max_size=10)
            await cls._ensure_tables()

    @classmethod
    async def _ensure_tables(cls):
        async with cls._pool.acquire() as conn:
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_articles (
                article_id TEXT PRIMARY KEY,
                link TEXT,
                title TEXT,
                processed_at TIMESTAMPTZ DEFAULT now()
            );
            """)

    @classmethod
    async def mark_processed(cls, article_id: str, link: str, title: str):
        async with cls._pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO processed_articles(article_id, link, title) VALUES($1,$2,$3) ON CONFLICT DO NOTHING",
                article_id, link, title
            )

    @classmethod
    async def is_processed(cls, article_id: str) -> bool:
        async with cls._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT article_id FROM processed_articles WHERE article_id = $1", article_id)
            return row is not None

