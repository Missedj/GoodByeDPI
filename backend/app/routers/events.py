from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import SessionLocal, engine, Base
router = APIRouter()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
@router.get("/events")
def list_events(account_id: int | None = None, limit: int = Query(200, le=500), db: Session = Depends(get_db)):
    q = db.execute("""SELECT id, account_id, level, code, meta_json, created_at FROM events
                     WHERE (:aid IS NULL OR account_id = :aid)
                     ORDER BY id DESC LIMIT :lim""", {"aid": account_id, "lim": limit})
    return [dict(r._mapping) for r in q]
