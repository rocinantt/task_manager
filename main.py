import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

import models
from database import Base, engine
from routers.tasks import router as tasks_router
from routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    for attempt in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            print("Подключились к базе")
            break
        except OperationalError:
            print(f"База пока  не готова, (попытка {attempt + 1})")
            time.sleep(3)
    yield


app = FastAPI(title="Task Manager API", lifespan=lifespan)

app.include_router(tasks_router)
app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")