from fastapi import APIRouter
from . import _flags_core as core
router = APIRouter()
@router.get("/flags")
def get_flags(): return core.get_all()
@router.post("/flags")
def set_flags(payload: dict): core.update(payload or {}); return core.get_all()
