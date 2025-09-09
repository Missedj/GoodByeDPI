import time, random
from typing import Tuple
from redis import Redis
class TokenBucket:
    def __init__(self, redis: Redis, prefix: str = "tb:"):
        self.r = redis; self.prefix = prefix
    def _keys(self, key: str):
        return f"{self.prefix}{key}:tokens", f"{self.prefix}{key}:ts"
    def consume(self, key: str, capacity: float, refill_per_sec: float, cost: float = 1.0) -> Tuple[bool, float]:
        tkey, tskey = self._keys(key)
        pipe = self.r.pipeline()
        now = time.time()
        pipe.get(tkey); pipe.get(tskey)
        tokens, last_ts = pipe.execute()
        tokens = float(tokens) if tokens else capacity
        last_ts = float(last_ts) if last_ts else now
        elapsed = max(0.0, now - last_ts)
        tokens = min(capacity, tokens + elapsed * refill_per_sec)
        allowed = tokens >= cost
        if allowed:
            tokens -= cost; wait = 0.0
        else:
            deficit = cost - tokens
            wait = deficit / refill_per_sec if refill_per_sec > 0 else 5.0
        pipe.set(tkey, tokens); pipe.set(tskey, now); pipe.execute()
        return allowed, wait + random.uniform(0, 0.4)
