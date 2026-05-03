from fastapi import APIRouter, Query, Depends
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.mantenimiento import ManttoRequest,MattoParams
from src.services.mantenimiento_service import set_mantto,search,get_Mtto
from src.models.auth import TokenResponse
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/mantenimientos", tags=["mantenimientos"])
# Esta ocurriendo un erro en esta parte, muy probablemente con los formatos del datetime.

#@router.get ( "/")
#async def buscar_mantenimiento (
#    idOrden:Optional[int]= Query(None),
#    tipo:Optional[str]=Query(None),
#    Fi:Optional[datetime]=Query(None),
#    Ff:Optional[datetime]=Query(None),
#    rPor:Optional[int]=Query(None),
#    vPor:Optional[int]=Query(None),
#    externo:Optional[bool]=Query(None),
#    rPorExt:Optional[int]=Query(None)    
#    ):
#    return await search(idOrden,tipo,Fi,Ff,rPor,vPor,externo,rPorExt)

@router.get ( "/")
async def buscar_mantenimiento (
    filters: MattoParams = Depends(), 
    limit: int = Query(10, ge=1, le=50), # Validamos min 1, max 50
    page: int = Query(1, ge=1)           # Página actual
):
    # Calculamos el offset (ej: página 1 -> offset 0, página 2 -> offset 10)
    offset = (page - 1) * limit
    
    # Convertimos el modelo a dict filtrando los None
    query_data = filters.model_dump(exclude_none=True)

    return await search(query_data,limit, offset)

@router.get("/{idMantenimiento}")
async def obtener_Mantenimiento(idMantenimiento:int):
    return await get_Mtto(idMantenimiento)

@router.post("/")
async def mantenimiento( mantto:ManttoRequest):
    return await set_mantto(mantto)
