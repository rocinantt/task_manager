from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    pending = "в ожидании"
    in_progress = "в работе"
    done = "завершено"


# --- Задачи ---

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.pending
    priority: int = Field(default=1, ge=1, le=5)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True


# --- Пользователи ---

class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# --- Токен ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
