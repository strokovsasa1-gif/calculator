from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import math
app = FastAPI(title="Calculator")

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Общее количество запросов к приложению",
    ["endpoint"]
)

START_TIME = time.time()

@app.get("/", response_class=HTMLResponse)
def index():
    REQUEST_COUNT.labels(endpoint="/").inc()
    with open("app/static/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/api/calc")
def calculate(a: float, b: float, op: str):
    REQUEST_COUNT.labels(endpoint="/api/calc").inc()
    if op == "add":
        result = a + b
    elif op == "sub":
        result = a - b
    elif op == "mul":
        result = a * b
    elif op == "div":
        result = a / b if b != 0 else None
    else:
        return {"error": "unknown operation"}

    if result is not None and (math.isinf(result) or math.isnan(result)):
        return {"error": "result too large or undefined"}

    return {"result": result}

# Health check: сервис жив и отвечает
@app.get("/health")
def health():
    return {"status": "ok", "uptime_seconds": round(time.time() - START_TIME, 1)}

# Метрики для Prometheus 
@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)