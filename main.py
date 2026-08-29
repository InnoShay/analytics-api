from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from collections import defaultdict
import numpy as np

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_KEY = "ak_relr3o507bdft10bjag3iyaa"
EMAIL = "24f2006027@ds.study.iitm.ac.in"

ALLOWED_ORIGINS = {"https://exam.sanand.workers.dev", "*"}

app = FastAPI()


# ---------------------------------------------------------------------------
# Middleware — CORS
# ---------------------------------------------------------------------------
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")

    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": origin if origin else "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "X-API-Key, Content-Type",
            "Access-Control-Max-Age": "600",
        }
        return JSONResponse(status_code=200, content={}, headers=headers)

    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
    response.headers["Access-Control-Allow-Headers"] = "X-API-Key, Content-Type"
    return response


# ---------------------------------------------------------------------------
# POST /analytics
# ---------------------------------------------------------------------------
@app.post("/analytics")
async def analytics(request: Request):
    # Auth check
    api_key = request.headers.get("x-api-key")
    if not api_key or api_key != API_KEY:
        return JSONResponse(status_code=401, content={"error": "unauthorized"})

    # Parse body
    body = await request.json()
    events = body.get("events", [])

    # Aggregations
    total_events = len(events)
    unique_users = len(set(e["user"] for e in events))

    # Revenue: sum of amount where amount > 0
    revenue = sum(e["amount"] for e in events if e["amount"] > 0)

    # Top user: user with highest positive-amount total
    user_totals: dict[str, float] = defaultdict(float)
    for e in events:
        if e["amount"] > 0:
            user_totals[e["user"]] += e["amount"]

    top_user = max(user_totals, key=user_totals.get) if user_totals else ""

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }
