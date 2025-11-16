# workflow + activities
# Minimal Temporal workflow + activity definitions
# Worker runs the activities (see worker.py)
from temporalio import workflow, activity
from temporalio.client import Client
import os, uuid, asyncio

TEMPORAL_ADDR = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "processing-task-queue")

# Activities: small wrappers that will be executed by worker
@activity.defn
async def activity_classify_relevance(article: dict) -> dict:
    # TODO: call Filter service / ML model or simple keyword heuristics
    title = article.get("title", "") or ""
    link = article.get("link", "")
    score = 0.0
    # naive keyword check
    keywords = ["ai","AI","trí tuệ nhân tạo","ứng dụng AI"]
    text = (title + " " + article.get("raw", {}).get("summary",""))[:1000].lower()
    for k in keywords:
        if k.lower() in text:
            score += 1.0
    return {"relevance_score": score, "route_to_ai": score>0}

@activity.defn
async def activity_emit_to_ai(article: dict):
    # publish to a stream / topic for AI layer to pick up
    from app.publisher import publish_for_ai
    await publish_for_ai({"article": article})
    return True

@workflow.defn
class ProcessArticleWorkflow:
    @workflow.run
    async def run(self, article: dict):
        # step 1: classify
        classification = await workflow.execute_activity(activity_classify_relevance, article, start_to_close_timeout=timedelta(seconds=20))
        # step 2: if relevant -> send to AI pipeline
        if classification.get("route_to_ai"):
            await workflow.execute_activity(activity_emit_to_ai, article, start_to_close_timeout=timedelta(seconds=20))
        # finish (could return metadata)
        return {"status": "ok", "classification": classification}

# helper to start workflows from consumer
async def start_process_workflow(article: dict) -> str:
    client = await Client.connect(TEMPORAL_ADDR)
    wf_id = f"process-{article.get('id') or str(uuid.uuid4())}"
    handle = await client.start_workflow(ProcessArticleWorkflow.run, article, id=wf_id, task_queue=TASK_QUEUE)
    return handle.id

