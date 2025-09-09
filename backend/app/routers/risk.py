from fastapi import APIRouter
from ..redis_conn import get_redis
router = APIRouter()
@router.get("/risk/weights")
def list_weights():
    r = get_redis()
    return { k.decode().split(":")[-1]: float(v.decode()) for k,v in r.hgetall("risk:overrides").items() } if r.exists("risk:overrides") else {}
@router.post("/risk/weights")
def set_weight(payload: dict):
    r = get_redis()
    acc = int(payload.get('account_id'))
    weight = float(payload.get('weight',1.0))
    r.hset("risk:overrides", f"acc:{acc}", weight)
    return {"ok": True}
