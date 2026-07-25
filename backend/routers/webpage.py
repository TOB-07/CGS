from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR/"frontend"/"static"

router = APIRouter()

router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@router.get("/")
async def index():
    return FileResponse("frontend/index.html")

@router.get("/dashboard")
async def dashboard():
    return FileResponse("frontend/dashboard.html")