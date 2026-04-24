from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.login import UserRequest, LoginRequest
from src.services.login_service import user_exists

router = APIRouter(prefix="/login", tags=["login"])

@router.post("/user")
async def user(user_datos:UserRequest):
  return await user_exists(user_datos)


@router.get("/login")
async def root():
    return {"message": "Hello World"}