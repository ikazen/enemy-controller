from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.web.routes import router

_root = Path(__file__).parent.parent

app = FastAPI(title="enemy-controller")
app.mount("/static", StaticFiles(directory=_root / "app" / "static"), name="static")
app.include_router(router)
