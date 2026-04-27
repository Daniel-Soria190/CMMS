from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.login import UserRequest, LoginRequest
from src.services.login_service import user_exists, password_match

router = APIRouter(prefix="/login", tags=["login"])

@router.get("/user/")
async def user(q: str):

  return await user_exists(q) #modificar la funcion para retornal el salt y username


@router.post("/login")
async def login(login_password:LoginRequest):
    return await password_match(login_password)