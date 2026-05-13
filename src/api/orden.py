from fastapi import APIRouter, Query, Depends
from fastapi import HTTPException
from typing import Optional

from src.models.orden import (
    ordenRequest, ordenParams, ordenUpdate,
    ReporteOrdenRequest, ReporteOrdenResponse,
    AsignarOrdenRequest, AsignarOrdenResponse,
)
from src.services.orden_service import (
    set_orden, search, get_orden, update,
    crear_reporte_orden,
    asignar_orden,
)
from src.services.auth_service import require_role, get_usuario_opcional


router = APIRouter(prefix="/orden", tags=["orden"])


@router.get("/")
async def buscar_orden(
    filters: ordenParams = Depends(),
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=1),
    current_user: dict = Depends(require_role(4))
):
    offset = (page - 1) * limit
    query_data = filters.model_dump(exclude_none=True)
    return await search(query_data, limit, offset)


@router.get("/{idOrden}")
async def obtener_orden(
    idOrden: int,
    current_user: dict = Depends(require_role(4))
):
    return await get_orden(idOrden)


@router.patch("/{idOrden}")
async def update_orden(
    idOrden: int,
    filter: ordenUpdate = Depends(),
    current_user: dict = Depends(require_role(4))
):
    data = filter.model_dump(exclude_none=True)
    return await update(idOrden, data)


@router.post("/")
async def orden(
    orden: ordenRequest,
    current_user: dict = Depends(require_role(4))
):
    return await set_orden(orden)


@router.post(
    "/reporte",
    response_model=ReporteOrdenResponse,
    status_code=201,
    summary="Crear orden de trabajo desde reporte (público o autenticado)",
)
async def crear_orden_reporte(
    body: ReporteOrdenRequest,
    id_usuario: Optional[int] = Depends(get_usuario_opcional),
):
    return await crear_reporte_orden(
        id_equipo_instalado=body.idEquipoInstalado,
        descripcion_fallo=body.descripcionFallo,
        prioridad=body.prioridad,
        id_usuario=id_usuario,
        contacto=body.contacto.model_dump() if body.contacto else None,
    )

# Agregar al final del router
@router.patch(
    "/{idOrden}/asignar",
    response_model=AsignarOrdenResponse,
    summary="Asignar técnico a una orden de trabajo",
)
async def asignar_orden_route(
    idOrden: int,
    body: AsignarOrdenRequest,
    current_user: dict = Depends(require_role(2)),  # Encargado de área o superior
):
    """
    Asigna un técnico a la OT y crea automáticamente el registro de Mantenimiento.

    Acceso:
    -------
    Requiere rol 2 (Encargado de Área) o superior.

    Parámetros:
    -----------
    idOrden : int (path)
        PK de la OrdenTrabajo a asignar.
    body.asignadoA : int
        FK → Usuario.idUsuario del técnico asignado.

    Errores:
    --------
    404 — OT o usuario no encontrado.
    409 — OT no está en estado 'por_asignar'.
    403 — Rol insuficiente.
    """
    return await asignar_orden(
        id_orden=idOrden,
        id_asignado=body.asignadoA,
    )