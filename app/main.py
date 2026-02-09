# app/main.py

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import json
import time
import asyncio
from pydantic import BaseModel

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from utils.logger import logger
from utils.cache import (
    redis_cache,
    cache_miss_event,
    CACHE_HITS_KEY,
    CACHE_MISSES_KEY,
    r
)
from utils.observer import Listener

logger.info("🔥 main.py loaded")

MAX_CACHE_LOGS = 100

# ---------------- ENV ---------------- #

load_dotenv()

# ---------------- APP ---------------- #

app = FastAPI(
    title=os.getenv("APP_NAME", "High-Performance App"),
    version="1.0.0"
)

# ---------------- RATE LIMITER ---------------- #

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"}
    )

# ---------------- OBSERVER ---------------- #

class CacheMissLogger(Listener):
    def update(self, data):
        print(f"[CacheMissLogger] {data}")
        log_entry = {"event": "cache_miss", "message": data}
        r.lpush("logs:cache", json.dumps(log_entry))
        r.ltrim("logs:cache", 0, MAX_CACHE_LOGS - 1)

cache_miss_event.register(CacheMissLogger())
logger.info("✅ CacheMissLogger registered")

# ---------------- CACHE ---------------- #

@redis_cache(ttl=60)
async def fetch_large_data(param: int):
    logger.info(f"Fetching data for {param}...")
    await asyncio.sleep(0.1)
    return {"result": f"Expensive Result for {param}"}

# ---------------- BACKGROUND TASK ---------------- #

class EmailRequest(BaseModel):
    email: str

async def send_email_task(email: str):
    await asyncio.sleep(1)
    logger.info(f"📧 Email sent to {email}")

# ---------------- ROUTES ---------------- #

@app.get("/")
def root():
    return {"status": "running", "message": "Week 6 live 🚀"}

@app.get("/data/{param}")
@limiter.limit("5/minute")
async def get_data(param: int, request: Request):
    logger.info("/data endpoint called")
    return await fetch_large_data(param)

@app.post("/send-email")
async def send_email(
    req: EmailRequest,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email_task, req.email)
    return {"status": "Email scheduled"}


@app.get("/metrics")
def metrics():
    return {
        "cache_hits": int(r.get(CACHE_HITS_KEY) or 0),
        "cache_misses": int(r.get(CACHE_MISSES_KEY) or 0),
    }

@app.get("/dashboard")
def dashboard():
    logs = {}

    for key in r.keys("logs:*"):
        entries = []
        for entry in r.lrange(key, 0, MAX_CACHE_LOGS - 1):
            try:
                entries.append(json.loads(entry))
            except json.JSONDecodeError:
                entries.append({"raw": entry})

        logs[key.replace("logs:", "")] = entries

    return {
        "cache_hits": int(r.get(CACHE_HITS_KEY) or 0),
        "cache_misses": int(r.get(CACHE_MISSES_KEY) or 0),
        "recent_events": logs,
    }

@app.get("/clear-cache")
def clear_cache():
    r.flushdb()
    return {"status": "cache cleared"}

@app.get("/health")
def health():
    try:
        if not r.ping():
            raise HTTPException(status_code=503, detail="Redis not available")
        return {"status": "ok", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis error: {e}")

# ---------------- MIDDLEWARE ---------------- #

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)

    logger.info(f"{request.method} {request.url.path} took {duration}ms")
    response.headers["X-Response-Time-ms"] = str(duration)
    return response
