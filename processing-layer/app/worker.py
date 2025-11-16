# temporal worker entry
import asyncio, os
from temporalio.worker import Worker
from temporalio.client import Client
from app.temporal_workflow import ProcessArticleWorkflow, activity_classify_relevance, activity_emit_to_ai

TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "processing-task-queue")
TEMPORAL_ADDR = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")

async def run_worker():
    client = await Client.connect(TEMPORAL_ADDR)
    worker = Worker(client, task_queue=TASK_QUEUE, workflows=[ProcessArticleWorkflow], activities=[activity_classify_relevance, activity_emit_to_ai])
    print("Temporal worker starting ...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(run_worker())

