# FastAPI app (API Gateway + Trigger controller)
import asyncio
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from app.config import settings
from app.scheduler import start_scheduler
from app.workers.rss_fetcher import run_all_feed_sources
from app.workers.scraper import fetch_and_publish
from app.publishers.message_bus import KafkaPublisher
import uvicorn

app = FastAPI(title="Input Layer - Trigger Controller")

# simple API-key auth dependency
def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

@app.on_event("startup")
async def startup_event():
    # start scheduler
    start_scheduler()
    # start kafka publisher if needed
    if settings.PUBLISHER == "kafka":
        app.state.kafka = KafkaPublisher()
        await app.state.kafka.start()

@app.on_event("shutdown")
async def shutdown_event():
    if settings.PUBLISHER == "kafka" and getattr(app.state, "kafka", None):
        await app.state.kafka.stop()

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.post("/trigger/rss", dependencies=[Depends(check_api_key)])
async def trigger_rss(background: BackgroundTasks):
    # trigger an on-demand run
    background.add_task(run_all_feed_sources)
    return {"status":"scheduled"}

from fastapi import Depends
@app.post("/trigger/fetch", dependencies=[Depends(check_api_key)])
async def trigger_fetch(url: str):
    # fetch a single URL (manual)
    doc = await fetch_and_publish(url)
    return {"status":"ok","url":doc["url"]}

@app.get("/sources", dependencies=[Depends(check_api_key)])
def list_sources():
    return {"rss": settings.RSS_SOURCES}
