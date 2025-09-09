from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse, JSONResponse
from ..redis_conn import get_redis
import configparser, io, json
router = APIRouter()
KEY = "config:kv"
@router.get("/config")
def get_config():
    r = get_redis()
    data = { k.decode(): v.decode() for k,v in r.hgetall(KEY).items() } if r.exists(KEY) else {}
    return data
@router.get("/config/export", response_class=PlainTextResponse)
def export_ini():
    r = get_redis()
    items = { k.decode(): v.decode() for k,v in r.hgetall(KEY).items() } if r.exists(KEY) else {}
    cp = configparser.ConfigParser()
    for full_key, val in items.items():
        if ":" in full_key:
            sec, key = full_key.split(":", 1)
        else:
            sec, key = "DEFAULT", full_key
        if sec not in cp: cp[sec] = {}
        cp[sec][key] = val
    buf = io.StringIO()
    cp.write(buf)
    return buf.getvalue()
@router.post("/config/merge")
def merge_ini(raw: str = Body(..., media_type="text/plain")):
    r = get_redis()
    cp = configparser.ConfigParser()
    cp.read_string(raw)
    added = 0; skipped = 0
    pipe = r.pipeline()
    old = { k.decode(): v.decode() for k,v in r.hgetall(KEY).items() } if r.exists(KEY) else {}
    for sec in cp.sections():
        for key, val in cp[sec].items():
            full = f"{sec}:{key}"
            if full in old:
                skipped += 1
            else:
                pipe.hset(KEY, full, val); added += 1
    pipe.execute()
    return {"ok": True, "added": added, "skipped": skipped, "total": added+skipped}
