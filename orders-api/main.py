from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import time
import base64

app = FastAPI()

TOTAL_ORDERS = 45
RATE_LIMIT = 19
WINDOW = 10  # seconds

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Fixed catalog
# -----------------------------
catalog = [
    {
        "id": i,
        "item": f"Item {i}",
        "price": float(i * 10)
    }
    for i in range(1, TOTAL_ORDERS + 1)
]

# -----------------------------
# Idempotency storage
# -----------------------------
idempotency = {}

# -----------------------------
# Rate limit storage
# -----------------------------
client_requests = {}


class Order(BaseModel):
    item: str
    quantity: int


# -----------------------------
# Cursor helpers
# -----------------------------
def encode_cursor(idx: int):
    return base64.urlsafe_b64encode(str(idx).encode()).decode()


def decode_cursor(cur: Optional[str]):
    if not cur:
        return 0
    try:
        return int(base64.urlsafe_b64decode(cur.encode()).decode())
    except Exception:
        return 0


# -----------------------------
# Rate limiting middleware
# -----------------------------
@app.middleware("http")
async def limiter(request, call_next):

    client = request.headers.get("X-Client-Id", "anonymous")

    now = time.time()

    arr = client_requests.setdefault(client, [])

    arr[:] = [t for t in arr if now - t < WINDOW]

    if len(arr) >= RATE_LIMIT:
        retry = WINDOW - (now - arr[0])
        if retry < 1:
            retry = 1

        return Response(
            status_code=429,
            headers={
                "Retry-After": str(int(retry))
            }
        )

    arr.append(now)

    return await call_next(request)


# -----------------------------
# POST /orders
# -----------------------------
@app.post("/orders", status_code=201)
def create_order(
    order: Order,
    idempotency_key: str = Header(..., alias="Idempotency-Key")
):

    if idempotency_key in idempotency:
        return idempotency[idempotency_key]

    obj = {
        "id": str(uuid.uuid4()),
        "item": order.item,
        "quantity": order.quantity
    }

    idempotency[idempotency_key] = obj

    return obj


# -----------------------------
# GET /orders
# -----------------------------
@app.get("/orders")
def list_orders(limit: int = 10, cursor: Optional[str] = None):

    start = decode_cursor(cursor)

    end = min(start + limit, TOTAL_ORDERS)

    items = catalog[start:end]

    next_cursor = None

    if end < TOTAL_ORDERS:
        next_cursor = encode_cursor(end)

    return {
        "items": items,
        "next_cursor": next_cursor
    }