from fastapi import APIRouter, Query
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.mantenimiento import ManttoRequest
from src.services.mantenimiento_service import set_mantto
from src.models.auth import TokenResponse
from typing import Optional


router = APIRouter(prefix="/mantenimientos", tags=["mantenimientos"])

@router.post("/mantenimiento/")
async def mantto( mantto:ManttoRequest):
    return await set_mantto(mantto )
