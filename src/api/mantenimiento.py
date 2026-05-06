from fastapi import APIRouter, Query, Depends
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.mantenimiento import MattoRequest,MattoParams,MattoUpdate
from src.services.mantenimiento_service import set_mantto,search,get_Mtto,update
from src.models.auth import TokenResponse
from typing import Optional
from datetime import datetime
from src.services.auth_service import require_role

router = APIRouter(prefix="/mantenimientos", tags=["mantenimientos"])


@router.get ( "/")
async def buscar_mantenimiento (
    filters: MattoParams = Depends(), 
    limit: int = Query(10, ge=1, le=50), # Validamos min 1, max 50
    page: int = Query(1, ge=1),           # Página actual
    current_user: dict = Depends(require_role(3))
):
    # Calculamos el offset (ej: página 1 -> offset 0, página 2 -> offset 10)
    offset = (page - 1) * limit
    
    # Convertimos el modelo a dict filtrando los None
    query_data = filters.model_dump(exclude_none=True)

    return await search(query_data,limit, offset)


@router.get("/{idMantenimiento}")
async def obtener_mantenimiento(idMantenimiento:int,
        current_user: dict = Depends(require_role(3))
        ):
    return await get_Mtto(idMantenimiento)


@router.patch ("/{idMantenimiento}")
async def update_matto(idMantenimiento:int ,
                       filter:MattoUpdate=Depends(),
                       current_user: dict = Depends(require_role(3))
                       ):
    data=filter.model_dump(exclude_none=True)
    return await update(idMantenimiento,data)


@router.post("/")
async def mantenimiento( mantto:MattoRequest,
        current_user: dict = Depends(require_role(3))
                        ):
    return await set_mantto(mantto)
