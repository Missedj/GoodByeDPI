from ..redis_conn import get_redis
DEFAULTS = {"global_cap":60,"global_rps":0.5,"account_cap":30,"account_rps":0.3,"peer_cap":10,"peer_rps":0.2,"autowarmup":0,"auto_profile":1,"active_hours":"09-22","timezone":"UTC"}
KEY = "flags:limits"
def get_all():
    r = get_redis(); data = r.hgetall(KEY) or {}; parsed = {}
    for k,v in data.items():
        try: parsed[k.decode()] = float(v.decode())
        except: parsed[k.decode()] = v.decode()
    out = DEFAULTS.copy(); out.update(parsed); return out
def update(payload: dict):
    r = get_redis(); p = r.pipeline()
    for k,v in (payload or {}).items():
        if k in DEFAULTS:
            try: p.hset(KEY,k,float(v))
            except: p.hset(KEY,k=str(v))
    p.execute()
