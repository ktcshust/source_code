"""
MAIN ENTRY POINT – AI News Intelligence System
----------------------------------------------

This file:
1. Loads environment & settings
2. Initializes Observability (logging, tracing, metrics)
3. Performs system health checks (Redis / Postgres / Kafka / Temporal / MinIO)
4. Boots Layers 1–6 (optional local mode)
5. Provides CLI commands:
    - python main.py --diag
    - python main.py --service input
    - python main.py --service processing
    - python main.py --service ai
    - python main.py --start-all
"""

import argparse
import asyncio
import sys
import os
import time
import importlib
from observability_layer.app.logging import log, configure_logging
from observability_layer.app.tracing import init_tracing
from observability_layer.app.metrics import set_up_metrics_server

# ---------  Layer-6 health check helpers ----------
async def check_redis():
    import redis
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        log.info("redis_ok")
        return True
    except Exception as e:
        log.error("redis_fail", error=str(e))
        return False

async def check_postgres():
    import asyncpg
    try:
        conn = await asyncpg.connect(os.getenv("PG_URI", "postgresql://postgres:postgres@localhost:5432/ai_news"))
        await conn.close()
        log.info("postgres_ok")
        return True
    except Exception as e:
        log.error("postgres_fail", error=str(e))
        return False

# async def check_kafka():
#     from aiokafka import AIOKafkaProducer
#     try:
#         producer = AIOKafkaProducer(bootstrap_servers=os.getenv("KAFKA_URL", "localhost:9092"))
#         await producer.start()
#         await producer.stop()
#         log.info("kafka_ok")
#         return True
#     except Exception as e:
#         log.error("kafka_fail", error=str(e))
#         return False

async def check_temporal():
    import httpx
    url = os.getenv("TEMPORAL_URL", "http://localhost:7233")
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            res = await client.get(url)
        log.info("temporal_ok")
        return True
    except Exception as e:
        log.error("temporal_fail", error=str(e))
        return False

async def full_diagnostics():
    log.info("=== RUNNING SYSTEM DIAGNOSTICS ===")
    results = {
        "redis":     await check_redis(),
        "postgres":  await check_postgres(),
        # "kafka":     await check_kafka(),
        "temporal":  await check_temporal(),
    }
    log.info("diagnostics_result", results=results)
    print("\nDiagnostic summary:")
    for name, status in results.items():
        print(f" - {name}: {'OK' if status else 'FAIL'}")

    if all(results.values()):
        print(">> All systems GO ✓")
    else:
        print(">> Issues detected ✗")
    return all(results.values())

# ---------  Run services (local mode) ----------
async def run_service(name: str):
    log.info("service_start", service=name)

    module_map = {
        "input":       "input_layer.run",
        "processing":  "processing_layer.run",
        "ai":          "ai_layer.run",
        "db":          "database_layer.run",
        "output":      "output_layer.run",
        "control":     "observability_layer.app.control_api",
    }

    if name not in module_map:
        raise ValueError(f"Unknown service name: {name}")

    module_path = module_map[name]
    module = importlib.import_module(module_path)

    if hasattr(module, "main"):
        await module.main()
    elif hasattr(module, "app"):  
        import uvicorn
        uvicorn.run(module.app, host="0.0.0.0", port=8000)
    else:
        log.error("service_no_entry_found", module=module_path)
        return

# ---------  Start all services in local multi-process mode ----------
async def start_all():
    log.info("start_all_services")

    tasks = [
        run_service("input"),
        run_service("processing"),
        run_service("ai"),
        run_service("db"),
        run_service("output"),
        run_service("control"),
    ]
    await asyncio.gather(*tasks)

# ---------  MAIN ENTRY ----------
async def main():
    configure_logging()
    init_tracing(service_name="system-entry")
    set_up_metrics_server(port=8015)

    parser = argparse.ArgumentParser(description="AI News System Entry Point")
    parser.add_argument("--diag",        action="store_true", help="Run full system diagnostics")
    parser.add_argument("--service",     type=str, help="Run a specific service")
    parser.add_argument("--start-all",   action="store_true", help="Run all services in local mode")
    parser.add_argument("--version",     action="store_true", help="Show system version")

    args = parser.parse_args()

    if args.version:
        print("AI News Intelligence System — version 1.0.0")
        return

    if args.diag:
        ok = await full_diagnostics()
        if not ok:
            sys.exit(1)
        return

    if args.service:
        await run_service(args.service)
        return

    if args.start_all:
        await start_all()
        return

    parser.print_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
