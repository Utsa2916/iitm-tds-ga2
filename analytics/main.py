from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

API_KEY = "ak_1rp3jbjw7ek6n9zuegeqqtl5"
EMAIL = "24f2008449@ds.study.iitm.ac.in"   # <-- Replace with your exam email

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


@app.post("/analytics")
def analytics(
    data: AnalyticsRequest,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    total_events = len(data.events)
    unique_users = len({e.user for e in data.events})

    revenue = 0.0
    user_totals = {}

    for e in data.events:
        if e.amount > 0:
            revenue += e.amount
            user_totals[e.user] = user_totals.get(e.user, 0) + e.amount

    top_user = max(user_totals, key=user_totals.get) if user_totals else ""

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }