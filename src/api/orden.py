from fastapi import APIRouter, Query
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.orden import ordenRequest
from src.services.orden_service import set_orden,search
from src.models.auth import TokenResponse
from typing import Optional
from datetime import datetime


router = APIRouter(prefix="/orden", tags=["orden"])

@router.get ( "/search/")
async def buscar_orden (
    idOrden: Optional[int] = Query(None),
    idEquipoInstall: Optional[int] = Query(None),
    prioridad: Optional[str] = Query(None),
    estado:Optional[str]=Query(None),
    fechaSoli:Optional[datetime]=Query(None),
    fechaEnt:Optional[datetime]=Query(None),
    asignadoa:Optional[int]=Query(None),
    creadopor:Optional[int]=Query(None),
    ):
    return await search (idOrden,idEquipoInstall,prioridad,estado,fechaSoli,fechaEnt,asignadoa,creadopor)


@router.post("/Crear orden/")
async def orden( orden:ordenRequest):
    return await set_orden(orden)