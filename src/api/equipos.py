from fastapi import APIRouter, Query, Depends
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.equipos import EquipoRequest,EquipoUpdate, EquipoParams
from src.services.equipos_service import set_equipo, get_Equipo, search, update
from src.models.auth import TokenResponse
from typing import Optional


router = APIRouter(prefix="/equipos", tags=["equipos"])

# @router.get ( "/")
# async def buscar_equipo (
#     nombre: Optional[str] = Query(None),
#     marca: Optional[str] = Query(None),
#     modelo: Optional[str] = Query(None)
# ):
#     return await search (nombre,marca,modelo)

@router.get("/")
async def buscar_equipo(
    filters: EquipoParams = Depends(),
    limit: int = Query(10, ge=1, le=50), # Validamos min 1, max 50
    page: int = Query(1, ge=1)           # Página actual
):
    # Calculamos el offset (ej: página 1 -> offset 0, página 2 -> offset 10)
    offset = (page - 1) * limit
    
    # Convertimos el modelo a dict filtrando los None
    query_data = filters.model_dump(exclude_none=True)
    
    return await search(query_data, limit, offset)

@router.get("/{idEquipo}")
async def obtener_equipo (idEquipo:int):
    return await get_Equipo(idEquipo)

@router.patch ("/{idEquipo}")
async def update_equipo(id:int ,equipo:EquipoUpdate):
    return await update(id,equipo)


@router.post("/")
async def equipo( equipo:EquipoRequest):
    return await set_equipo(equipo)

