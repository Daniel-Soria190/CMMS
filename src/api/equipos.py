from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.equipos import equipoRequest
from src.services.equipos_service import set_equipo
from src.models.auth import TokenResponse


router = APIRouter(prefix="/equipos", tags=["equipos"])

@router.post("/equipo/")
async def equipo( equipo:equipoRequest):
    return await set_equipo(equipo)

