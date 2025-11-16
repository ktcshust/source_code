# FastAPI: healthcheck + maintenance flags + control endpoints
# app/control_api.py
from fastapi import FastAPI, HTTPException
import asyncio
import os
from typing import Dict
from app.logging import log
from app.metrics import router as metrics_router, SERVICE_UP
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(title="Control API - Observability & Control")

# mount metrics route for convenience (optional)
app.include_router(metrics_router, prefix="")

@app.on_event("startup")
async def startup():
    SERVICE_UP.labels(service="control-api").set(1)
    log.info("control_api_startup")

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.post("/maintenance/{service_name}")
async def set_maintenance(service_name: str, enable: bool):
    key = f"maintenance:{service_name}"
    if enable:
        r.set(key, "1")
    else:
        r.delete(key)
    log.info("maintenance_flag_toggled", service=service_name, enable=enable)
    return {"service": service_name, "maintenance": enable}

@app.get("/maintenance/{service_name}")
async def get_maintenance(service_name: str):
    return {"service": service_name, "maintenance": bool(r.get(f"maintenance:{service_name}"))}

@app.post("/flag/{flag_name}")
async def set_flag(flag_name: str, value: str):
    r.set(f"flag:{flag_name}", value)
    log.info("flag_set", flag=flag_name, value=value)
    return {"flag": flag_name, "value": value}

@app.get("/flags")
async def list_flags():
    keys = r.keys("flag:*")
    return {k: r.get(k) for k in keys}
