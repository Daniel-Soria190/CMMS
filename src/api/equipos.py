from fastapi import APIRouter, Query
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.equipos import EquipoRequest,EquipoUpdate
from src.services.equipos_service import set_equipo, search, update
from src.models.auth import TokenResponse
from typing import Optional

router = APIRouter(prefix="/equipos", tags=["equipos"])

@router.get ( "/search/")
async def buscar_equipo (
    nombre: Optional[str] = Query(None),
    marca: Optional[str] = Query(None),
    modelo: Optional[str] = Query(None)
):
    return await search (nombre,marca,modelo)

@router.patch ("/equipos/{idEquipo}")
async def update_equipo(id:int ,equipo:EquipoUpdate):
    return await update(id,equipo)


@router.post("/equipo/")
async def equipo( equipo:EquipoRequest):
    return await set_equipo(equipo)

