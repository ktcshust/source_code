# Prometheus metrics helpers + standalone /metrics server
# app/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from prometheus_client import multiprocess, start_http_server
from fastapi import APIRouter, Response
import os

# global registry (each process can use same canonical names)
REQUEST_COUNT = Counter("app_http_requests_total", "Total HTTP requests", ["service", "method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("app_http_request_duration_seconds", "HTTP request latency seconds", ["service", "endpoint"])
IN_FLIGHT = Gauge("app_in_flight_requests", "In-flight requests", ["service"])
SERVICE_UP = Gauge("app_up", "Service up (1 = up)", ["service"])

router = APIRouter()

@router.get("/metrics")
async def metrics():
    # return prometheus metrics
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

def instrument_request(service_name: str, method: str, endpoint: str, status: str, duration: float):
    REQUEST_COUNT.labels(service=service_name, method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(service=service_name, endpoint=endpoint).observe(duration)

def set_up_metrics_server(port: int = 8009):
    # start a simple prometheus exposition server in a thread (if you prefer separate)
    start_http_server(port)
