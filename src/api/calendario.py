from fastapi import APIRouter, Depends, Query
from datetime import date
from src.models.orden import (
    CalendarioDiaResponse,
    CalendarioSemanaResponse,
    CalendarioMesResponse,
)
from src.services.calendario_service import (
    get_calendario_dia,
    get_calendario_semana,
    get_calendario_mes,
)
from src.services.auth_service import require_role

router = APIRouter(prefix="/calendario", tags=["calendario"])


@router.get(
    "/dia",
    response_model=CalendarioDiaResponse,
    summary="Detalle completo de órdenes para un día — tablero kanban",
)
async def calendario_dia(
    fecha: date = Query(..., description="Día consultado. Formato: YYYY-MM-DD"),
    current_user: dict = Depends(require_role(5)),
):
    """
    Retorna las 4 columnas del kanban para el día indicado.

    Acceso:
    -------
    Rol 1 (Admin)         → todas las órdenes, incluye por_asignar.
    Rol 2 (Enc. de Área)  → equipos de su área, incluye por_asignar.
    Rol >= 3 (Técnico)    → sus órdenes, por_asignar siempre vacío.
    """
    return await get_calendario_dia(
        fecha=fecha,
        id_rol=current_user["idRol"],
        id_area=current_user.get("idArea"),
        id_usuario=current_user["idUsuario"],
    )


@router.get(
    "/semana",
    response_model=CalendarioSemanaResponse,
    summary="Conteos por día para la semana — widget semanal",
)
async def calendario_semana(
    fecha: date = Query(..., description="Cualquier día de la semana. Formato: YYYY-MM-DD"),
    current_user: dict = Depends(require_role(5)),
):
    """
    Retorna conteos numéricos por categoría para cada día de la semana.
    Usado por WidgetCalendario.qml para pintar los badges.
    """
    return await get_calendario_semana(
        fecha=fecha,
        id_rol=current_user["idRol"],
        id_area=current_user.get("idArea"),
        id_usuario=current_user["idUsuario"],
    )


@router.get(
    "/mes",
    response_model=CalendarioMesResponse,
    summary="Conteos por día para el mes completo — widget mensual",
)
async def calendario_mes(
    fecha: date = Query(..., description="Cualquier día del mes. Formato: YYYY-MM-DD"),
    current_user: dict = Depends(require_role(5)),
):
    """
    Retorna conteos numéricos por categoría para cada día del mes.
    Usado por Calendario.qml para pintar cada celda del grid.
    """
    return await get_calendario_mes(
        fecha=fecha,
        id_rol=current_user["idRol"],
        id_area=current_user.get("idArea"),
        id_usuario=current_user["idUsuario"],
    )