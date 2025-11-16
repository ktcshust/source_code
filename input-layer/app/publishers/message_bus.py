import json
import asyncio
from typing import Any
from app.config import settings

# Redis publisher (async)
if settings.PUBLISHER == "redis":
    import redis.asyncio as redis

class RedisStreamPublisher:
    def __init__(self, stream_name="input:articles"):
        self.stream_name = stream_name
        self._client = redis.from_url(settings.REDIS_URL)

    async def publish(self, payload: dict):
        await self._client.xadd(self.stream_name, {"data": json.dumps(payload)}, maxlen=10000)

# Kafka publisher (aiokafka)
if settings.PUBLISHER == "kafka":
    from aiokafka import AIOKafkaProducer
    class KafkaPublisher:
        def __init__(self, topic="articles"):
            self.topic = topic
            self._producer = None

        async def start(self):
            if self._producer is None:
                self._producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP)
                await self._producer.start()

        async def publish(self, payload: dict):
            await self._producer.send_and_wait(self.topic, json.dumps(payload).encode('utf-8'))

        async def stop(self):
            if self._producer:
                await self._producer.stop()
