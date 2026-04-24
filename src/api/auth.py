from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.auth import SaltRequest, LoginRequest
from src.services.auth_service import get_salt, login

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/salt")
async def post_salt(data: SaltRequest):
    return await get_salt(data)
    
@router.post("/login")
async def post_login(data: LoginRequest):
    return await login(data)
    