from fastapi import APIRouter, Query, Depends, File, UploadFile, Request
from fastapi import HTTPException
from fastapi.responses import Response
from typing import Optional

from src.models.orden import (
    ordenRequest, ordenParams, ordenUpdate,
    ReporteOrdenRequest, ReporteOrdenResponse,   # nuevos
)
from src.services.orden_service import (
    set_orden, search, get_orden, update,
    crear_reporte_orden,                          # nuevo
)
from src.services.auth_service import require_role, get_usuario_opcional  # nuevo




router = APIRouter(prefix="/orden", tags=["orden"])


@router.get("/")
async def buscar_orden(
    filters: ordenParams = Depends(),
    limit: int = Query(10, ge=1, le=50), # Validamos min 1, max 50
    page: int = Query(1, ge=1),           # Página actual
    current_user: dict = Depends(require_role(4))
):
    # Calculamos el offset (ej: página 1 -> offset 0, página 2 -> offset 10)
    offset = (page - 1) * limit
    
    # Convertimos el modelo a dict filtrando los None
    query_data = filters.model_dump(exclude_none=True)
    
    return await search(query_data, limit, offset)


@router.get("/{idOrden}")
async def obtener_orden (idOrden:int,
        current_user: dict = Depends(require_role(4))
        ):
    return await get_orden(idOrden)


@router.patch ("/{idOrden}")
async def update_orden(idOrden:int ,
        filter:ordenUpdate=Depends(),
        current_user: dict = Depends(require_role(4))
        ):
    data= filter.model_dump(exclude_none=True)
    return await update(idOrden,data)


@router.post("/")
async def orden( orden:ordenRequest,
        current_user: dict = Depends(require_role(4))):
    return await set_orden(orden)

@router.post(
    "/reporte",
    response_model=ReporteOrdenResponse,
    status_code=201,
    summary="Crear orden de trabajo desde reporte (público o autenticado)",
)
async def crear_orden_reporte(
    request: Request,
    # Body JSON con los datos del reporte
    body: ReporteOrdenRequest,
    # Fotos opcionales — se envían como multipart si se incluyen
    fotos: list[UploadFile] = File(default=[]),
    # Token opcional — None si no hay sesión
    id_usuario: Optional[int] = Depends(get_usuario_opcional),
):
    return await crear_reporte_orden(
        id_equipo_instalado=body.idEquipoInstalado,
        descripcion_fallo=body.descripcionFallo,
        prioridad=body.prioridad,
        id_usuario=id_usuario,
        contacto=body.contacto.model_dump() if body.contacto else None,
        fotos=fotos,
    )