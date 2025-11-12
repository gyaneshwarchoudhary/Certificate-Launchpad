# app/api/routes/healthcheck.py
from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health():
    return {"status": "ok"}
