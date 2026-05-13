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
    summary="Órdenes de trabajo para un día específico",
)
async def calendario_dia(
    fecha: date = Query(..., description="Fecha consultada. Formato: YYYY-MM-DD"),
    current_user: dict = Depends(require_role(5)),
):
    """
    Retorna pendientes, en proceso y finalizadas para el día indicado.

    Acceso:
    -------
    Rol 1 (Admin)          → todas las órdenes.
    Rol 2 (Enc. de Área)   → solo equipos de su área.
    Rol >= 3 (Técnico)     → solo sus órdenes asignadas.

    Parámetros:
    -----------
    fecha : date
        Día a consultar. Formato YYYY-MM-DD.
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
    summary="Órdenes agrupadas por día para la semana que contiene la fecha",
)
async def calendario_semana(
    fecha: date = Query(..., description="Cualquier día de la semana. Formato: YYYY-MM-DD"),
    current_user: dict = Depends(require_role(5)),
):
    """
    Retorna un objeto con clave por día (lunes a domingo)
    con sus respectivas categorías de órdenes.
    Usado por WidgetCalendario.qml.
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
    summary="Órdenes agrupadas por día para el mes completo",
)
async def calendario_mes(
    fecha: date = Query(..., description="Cualquier día del mes. Formato: YYYY-MM-DD"),
    current_user: dict = Depends(require_role(5)),
):
    """
    Retorna un objeto con clave por cada día del mes
    con sus respectivas categorías de órdenes.
    Usado por Calendario.qml.
    """
    return await get_calendario_mes(
        fecha=fecha,
        id_rol=current_user["idRol"],
        id_area=current_user.get("idArea"),
        id_usuario=current_user["idUsuario"],
    )