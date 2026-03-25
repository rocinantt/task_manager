from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def get_users_stub():
    return {"message": "Users endpoint works"}