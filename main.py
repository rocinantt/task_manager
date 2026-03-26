from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
import models 
from routers.tasks import router as tasks_router
from routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Task Manager API", lifespan=lifespan)


app.include_router(tasks_router)
app.include_router(users_router)