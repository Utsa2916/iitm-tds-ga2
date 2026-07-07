from fastapi import FastAPI, Request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from collections import deque
import uuid
import time
from datetime import datetime

EMAIL = "24f2008449@ds.study.iitm.ac.in"  # Replace with your exam email

app = FastAPI()

start_time = time.time()

# Prometheus Counter
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

# Store last logs
logs = deque(maxlen=1000)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())

    http_requests_total.inc()

    log = {
        "level": "INFO",
        "ts": datetime.utcnow().isoformat() + "Z",
        "path": request.url.path,
        "request_id": request_id,
    }
    logs.append(log)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/work")
def work(n: int):
    # Simulate K units of work
    total = 0
    for i in range(n):
        total += i

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - start_time
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return list(logs)[-limit:]