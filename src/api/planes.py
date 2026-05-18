from fastapi import APIRouter, Depends, Query
from typing import Optional

from src.models.planes import PlanCreate, PlanUpdate, PlanResponse
from src.services.scheduler_service import (
    crear_plan,
    listar_planes,
    get_plan,
    actualizar_plan,
)
from src.services.auth_service import require_role

router = APIRouter(prefix="/planes", tags=["planes"])


@router.post(
    "/",
    response_model=PlanResponse,
    status_code=201,
    summary="Programar mantenimiento inicial para un equipo",
)
async def crear_plan_route(
    body: PlanCreate,
    current_user: dict = Depends(require_role(1)),  # Solo administrador
):
    return await crear_plan(body.model_dump(), current_user["idUsuario"])


@router.get(
    "/",
    summary="Listar planes de mantenimiento",
)
async def listar_planes_route(
    activo: Optional[bool] = Query(None),
    current_user: dict = Depends(require_role(2)),
):
    return await listar_planes(activo)


@router.get(
    "/{idPlan}",
    response_model=PlanResponse,
    summary="Detalle de un plan",
)
async def get_plan_route(
    idPlan: int,
    current_user: dict = Depends(require_role(2)),
):
    return await get_plan(idPlan)


@router.patch(
    "/{idPlan}",
    response_model=PlanResponse,
    summary="Sobreescribir fecha o pausar un plan",
)
async def actualizar_plan_route(
    idPlan: int,
    body: PlanUpdate,
    current_user: dict = Depends(require_role(1)),  # Solo administrador
):
    data = body.model_dump(exclude_none=True)
    return await actualizar_plan(idPlan, data)