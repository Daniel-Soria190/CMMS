from fastapi import APIRouter, Query
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.equipos import EquipoRequest,EquipoUpdate
from src.services.equipos_service import set_equipo, get_Equipo, search, update
from src.models.auth import TokenResponse
from typing import Optional

router = APIRouter(prefix="/equipos", tags=["equipos"])

@router.get ( "/")
async def buscar_equipo (
    nombre: Optional[str] = Query(None),
    marca: Optional[str] = Query(None),
    modelo: Optional[str] = Query(None)
):
    return await search (nombre,marca,modelo)

@router.get("/{idEquipo}")
async def obtener_equipo (idEquipo:int):
    return await get_Equipo(idEquipo)

@router.patch ("/{idEquipo}")
async def update_equipo(id:int ,equipo:EquipoUpdate):
    return await update(id,equipo)


@router.post("/")
async def equipo( equipo:EquipoRequest):
    return await set_equipo(equipo)

