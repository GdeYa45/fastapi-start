from fastapi import FastAPI
from src.api.hotels import router as router_hotels
from src.database import *

app = FastAPI()

app.include_router(router_hotels)
