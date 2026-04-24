from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response

router = APIRouter(prefix="/login", tags=["login"])

@router.get("/user")
async def root():
    return {"message": "Hello World"}

@router.get("/login")
async def root():
    return {"message": "Hello World"}