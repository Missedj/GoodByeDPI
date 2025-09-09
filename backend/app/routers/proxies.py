from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal, engine, Base
from .. import models, schemas
router = APIRouter()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
@router.get("/", response_model=list[schemas.ProxyOut])
def list_proxies(db: Session = Depends(get_db)):
    return db.query(models.Proxy).order_by(models.Proxy.id).all()
@router.post("/", response_model=schemas.ProxyOut)
def add_proxy(body: schemas.ProxyIn, db: Session = Depends(get_db)):
    p = models.Proxy(kind=body.kind, host=body.host, port=body.port, login=body.login, password=body.password)
    db.add(p); db.commit(); db.refresh(p); return p
