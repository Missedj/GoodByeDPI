from fastapi import APIRouter
from ..redis_conn import get_redis
import json
router = APIRouter()
@router.get("/proxy/sources")
def sources_get():
    r = get_redis(); raw = r.get("proxy:sources"); return json.loads(raw) if raw else []
@router.post("/proxy/sources")
def sources_set(sources: list[str]):
    r = get_redis(); r.set("proxy:sources", json.dumps(sources or [])); return {"ok": True, "count": len(sources)}
