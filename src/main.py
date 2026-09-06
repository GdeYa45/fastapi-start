from pathlib import Path

from fastapi import FastAPI
from src.api.hotels import router as router_hotels
from src.api.auth import router as router_auth
import sys

sys.path.append(str(Path(__file__).parent.parent))
app = FastAPI()
app.include_router(router_auth)

app.include_router(router_hotels)
