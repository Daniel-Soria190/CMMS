from fastapi import APIRouter, Query
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.mantenimiento import ManttoRequest
from src.services.mantenimiento_service import set_mantto,search
from src.models.auth import TokenResponse
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/mantenimientos", tags=["mantenimientos"])
# Esta ocurriendo un erro en esta parte, muy probablemente con los formatos del datetime.

@router.get ( "/search/")
async def buscar_mantenimiento (
    idOrden:Optional[int]= Query(None),
    tipo:Optional[str]=Query(None),
    Fi:Optional[datetime]=Query(None),
    Ff:Optional[datetime]=Query(None),
    rPor:Optional[int]=Query(None),
    vPor:Optional[int]=Query(None),
    externo:Optional[bool]=Query(None),
    rPorExt:Optional[int]=Query(None)
    
    ):
    return await search(idOrden,tipo,Fi,Ff,rPor,vPor,externo,rPorExt)

@router.post("/mantenimiento/")
async def mantto( mantto:ManttoRequest):
    return await set_mantto(mantto)
