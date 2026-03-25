from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/")
def get_tasks_stub():
    return {"message": "Tasks endpoint works"}