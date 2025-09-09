from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from redis import Redis
from rq import Queue
from ..db import SessionLocal, engine, Base
from .. import models, schemas
from common.config import settings
router = APIRouter()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
def get_queue():
    r = Redis.from_url(settings.redis_url); return Queue("jobs", connection=r)
@router.get("/", response_model=list[schemas.JobOut])
def list_jobs(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Job).order_by(models.Job.id.desc()).limit(limit).all()
@router.post("/", response_model=schemas.JobOut)
def enqueue_job(body: schemas.JobCreate, db: Session = Depends(get_db)):
    if body.kind not in {"inviter_optin","parser_owned","cloner_owned","warmup"}:
        raise HTTPException(status_code=400, detail="Unsupported job kind (safe ops only)")
    acc = db.query(models.Account).get(body.account_id)
    if not acc: raise HTTPException(status_code=404, detail="Account not found")
    row = models.Job(account_id=acc.id, kind=body.kind, payload_json=body.payload_json, state="ENQUEUED")
    db.add(row); db.commit(); db.refresh(row)
    get_queue().enqueue("worker.jobs.run_job", row.id, job_timeout=900)
    return row
