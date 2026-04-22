from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.users import UserRequest
from src.services.users_service import set_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post ("/user")
async def user(user: UserRequest):
    return await set_user(user)