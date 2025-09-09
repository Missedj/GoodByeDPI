from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
from common.config import settings
from ..db import SessionLocal, engine, Base
from .. import models, schemas
router = APIRouter()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
@router.get("/", response_model=list[schemas.AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(models.Account).order_by(models.Account.id).all()
@router.post("/", response_model=schemas.AccountOut)
def add_account(body: schemas.AccountIn, db: Session = Depends(get_db)):
    session_path = Path(settings.sessions_dir) / body.session_filename
    if not session_path.exists():
        raise HTTPException(status_code=400, detail="Session file not found")
    acc = models.Account(phone=body.phone, session_path=str(session_path), proxy_id=body.proxy_id, status="READY")
    db.add(acc); db.commit(); db.refresh(acc); return acc
@router.patch("/{account_id}", response_model=schemas.AccountOut)
def update_account(account_id: int, patch: dict, db: Session = Depends(get_db)):
    acc = db.query(models.Account).get(account_id)
    if not acc: raise HTTPException(status_code=404, detail="Account not found")
    if "proxy_id" in patch: acc.proxy_id = patch.get("proxy_id")
    if "status" in patch: acc.status = patch.get("status")
    db.add(acc); db.commit(); db.refresh(acc); return acc
