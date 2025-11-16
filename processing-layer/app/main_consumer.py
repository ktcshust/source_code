# entry: run_consumer
import asyncio
from app.consumer_redis import consumer_loop

if __name__ == "__main__":
    try:
        asyncio.run(consumer_loop())
    except KeyboardInterrupt:
        print("Shutting down consumer")

