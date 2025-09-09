from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal, engine, Base
from .. import models
router = APIRouter()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
@router.post("/proxy/assign_oneip")
def proxy_assign_oneip(db: Session = Depends(get_db)):
    rows = db.execute("""
        WITH good AS (SELECT id FROM proxies WHERE COALESCE(fail_streak,0)=0 ORDER BY last_ok_at DESC NULLS LAST, id DESC)
        SELECT a.id as aid, g.id as pid FROM accounts a JOIN good g ON TRUE WHERE a.proxy_id IS NULL LIMIT 100
    """)
    cnt = 0
    for aid, pid in rows:
        db.execute("UPDATE accounts SET proxy_id=:p WHERE id=:a AND proxy_id IS NULL", {"p": pid, "a": aid}); cnt += 1
    db.commit(); return {"ok": True, "assigned": cnt}
