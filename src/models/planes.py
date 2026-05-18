from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class PlanCreate(BaseModel):
    """
    Body para POST /planes/
    El admin programa el primer mantenimiento de un equipo.

    Campos:
    -------
    idEquipoInstalado : int
        FK → EquipoInstalado.idEquipoInstalado
    tipo : str
        'preventiva' o 'inspeccion'
    fechaInicio : date
        Fecha en que debe ejecutarse el primer mantenimiento.
        El scheduler usará esta como proximaEjecucion inicial.
    frecuenciaAuto : bool
        True  → el scheduler calcula frecuenciaDias desde VistaEquipoGE
        False → usa frecuenciaDias manual
    frecuenciaDias : Optional[int]
        Solo requerido si frecuenciaAuto = False
    """
    idEquipoInstalado: int
    tipo: str
    fechaInicio: date
    frecuenciaAuto: bool = True
    frecuenciaDias: Optional[int] = None


class PlanUpdate(BaseModel):
    """
    Body para PATCH /planes/{idPlan}
    Permite sobreescribir la próxima ejecución o pausar el plan.

    Campos:
    -------
    proximaEjecucionOverride : Optional[date]
        Sobreescribe la fecha calculada para la siguiente ejecución.
        El scheduler la consume y la limpia después de usarla.
    activo : Optional[bool]
        False → pausa el plan sin borrarlo.
    frecuenciaAuto : Optional[bool]
    frecuenciaDias : Optional[int]
    """
    proximaEjecucionOverride: Optional[date] = None
    activo: Optional[bool] = None
    frecuenciaAuto: Optional[bool] = None
    frecuenciaDias: Optional[int] = None


class PlanResponse(BaseModel):
    idPlan: int
    idEquipoInstalado: int
    tipo: str
    frecuenciaDias: Optional[int]
    ultimaEjecucion: Optional[date]
    proximaEjecucion: Optional[date]
    activo: bool
    frecuenciaAuto: bool
    proximaEjecucionOverride: Optional[date]
    creadoPor: Optional[int]
    fechaCreacion: Optional[datetime]
    idOrdenGenerada: Optional[int]