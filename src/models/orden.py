from pydantic import BaseModel, EmailStr
from datetime import datetime 
from typing import Optional

from fastapi import  Query


class ordenRequest(BaseModel):
    idEquipoInstall:int 
    descripcion:str
    prioridad:str
    estado:str
    fechaSoli:datetime
    asignadoa:int
    creadopor:int
    creadoporext:int

class ordenUpdate(BaseModel):
    descripcionFallo: Optional[str] = None
    prioridad: Optional[str] = None
    estado:Optional[str]=None
    fechaEntrega:Optional[datetime]=None
    asignadoA:Optional[int]=None

class ordenParams(BaseModel):

    idEquipoInstalado: Optional[int] = None
    prioridad: Optional[str] = None
    estado:Optional[str]=None
    fechaSolicitud:Optional[datetime]=None
    fechaEntrega:Optional[datetime]=None
    asignadoA:Optional[int]=None
    creadoPorUsuario:Optional[int]=None

# ── Modelos existentes (no se tocan) ─────────────────────────────────────────

# class ordenRequest(BaseModel):
#     idEquipoInstall: int
#     descripcion: str
#     prioridad: str
#     estado: str
#     asignadoa: Optional[int] = None
#     creadopor: Optional[int] = None
#     creadoporext: Optional[int] = None

# class ordenParams(BaseModel):
#     idEquipoInstalado: Optional[int] = None
#     prioridad: Optional[str] = None
#     estado: Optional[str] = None
#     fechaSolicitud: Optional[datetime] = None
#     FechaEntrega: Optional[datetime] = None
#     asignadoA: Optional[int] = None
#     creadoPorUsuario: Optional[int] = None

# class ordenUpdate(BaseModel):
#     idEquipoInstalado: Optional[int] = None
#     descripcionFallo: Optional[str] = None
#     prioridad: Optional[str] = None
#     estado: Optional[str] = None
#     fechaEntrega: Optional[datetime] = None
#     asignadoA: Optional[int] = None


# ── Modelos nuevos para el flujo de reporte ───────────────────────────────────

class ContactoExternoIn(BaseModel):
    """Datos del reportador anónimo."""
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    empresa: Optional[str] = None


class ReporteOrdenRequest(BaseModel):
    """
    Body del POST /orden/reporte
    Funciona con o sin token.
    Si hay token, contacto se ignora.
    Si no hay token, contacto es obligatorio.
    """
    idEquipoInstalado: int
    descripcionFallo: str
    prioridad: Optional[str] = "media"
    contacto: Optional[ContactoExternoIn] = None


class ReporteOrdenResponse(BaseModel):
    idOrden: int
    folio: str
    estado: str
    fechaSolicitud: datetime
    idEquipoInstalado: int
    creadoPorUsuario: Optional[int] = None
    creadoPorReportante: Optional[int] = None  # ← era creadoPorExterno
    archivosSubidos: int = 0
    mensaje: str

class AsignarOrdenRequest(BaseModel):
    """
    Body para PATCH /orden/{idOrden}/asignar.

    Campos:
    -------
    asignadoA : int
        FK → Usuario.idUsuario
        Técnico o ingeniero que ejecutará el mantenimiento.
        Debe existir en la tabla Usuario.
    """
    asignadoA: int


class AsignarOrdenResponse(BaseModel):
    """
    Respuesta de PATCH /orden/{idOrden}/asignar.

    Campos:
    -------
    idOrden : int
        PK de la orden de trabajo actualizada.
    idMantenimiento : int
        PK del registro Mantenimiento creado automáticamente.
    folio : str
        Folio legible de la OT. Formato: OT-YYYY-NNNNN.
    estado : str
        Nuevo estado de la OT.
        Check: ('por_asignar', 'asignada', 'en_proceso', 'finalizada', 'cancelada')
    asignadoA : int
        FK → Usuario.idUsuario del técnico asignado.
    mensaje : str
        Confirmación legible de la operación.
    """
    idOrden: int
    idMantenimiento: int
    folio: str
    estado: str
    asignadoA: int
    mensaje: str


from datetime import date


# ── Reemplazar los modelos de calendario existentes ───────────────────────────

class CalendarioItem(BaseModel):
    """
    Representa una orden de trabajo en el tablero diario.

    Campos:
    -------
    idOrden : int
        PK → OrdenTrabajo.idOrden
    idEquipoInstalado : int
        FK → EquipoInstalado.idEquipoInstalado
    idMantenimiento : Optional[int]
        FK → Mantenimiento.idMantenimiento
        Solo presente en 'en_proceso' y 'finalizado'.
    folio : Optional[str]
        Identificador legible. Formato: OT-YYYY-NNNNN
    nombre : str
        Nombre del equipo. FK → Equipo.nombre
    NoSerie : str
        UK → EquipoInstalado.numeroSerie
    Ubicacion : Optional[str]
        Ubicación física del equipo instalado.
    falla : Optional[str]
        Descripción del fallo. Solo en 'por_asignar' y 'asignada'.
    tecnico : Optional[str]
        Nombre completo del técnico. Solo en 'en_proceso'.
        FK → Usuario.idUsuario via OrdenTrabajo.asignadoA
    nota : Optional[str]
        Descripción del trabajo. Solo en 'finalizado'.
        FK → Mantenimiento.descripcionTrabajo
    """
    idOrden:           int
    idEquipoInstalado: int
    idMantenimiento:   Optional[int] = None
    folio:             Optional[str] = None
    nombre:            str
    NoSerie:           str
    Ubicacion:         Optional[str] = None
    falla:             Optional[str] = None
    tecnico:           Optional[str] = None
    nota:              Optional[str] = None


class CalendarioDiaResponse(BaseModel):
    """
    Respuesta de GET /calendario/dia — detalle completo del día.

    Columnas para Admin/Encargado (idRol <= 2):
        por_asignar, asignada, en_proceso, finalizado

    Columnas para Técnico (idRol >= 3):
        por_asignar y asignada siempre vacíos.
        Solo ve en_proceso y finalizado de sus órdenes.

    Campos:
    -------
    por_asignar : list[CalendarioItem]
        OTs sin técnico asignado con fechaSolicitud <= fecha consultada.
        Check estado = 'por_asignar'
    asignada : list[CalendarioItem]
        OTs asignadas pero no iniciadas con fechaSolicitud <= fecha consultada.
        Check estado = 'asignada'
    en_proceso : list[CalendarioItem]
        OTs actualmente en trabajo. Sin restricción de fecha.
        Check estado = 'en_proceso'
    finalizado : list[CalendarioItem]
        OTs cerradas ese mismo día.
        fechaCierre::date = fecha consultada.
        Check estado = 'finalizada'
    """
    por_asignar: list[CalendarioItem]
    asignada:    list[CalendarioItem]
    en_proceso:  list[CalendarioItem]
    finalizado:  list[CalendarioItem]


class ResumenDia(BaseModel):
    """
    Conteos por categoría para un día — usado en widgets semana y mes.

    Campos:
    -------
    por_asignar : int
        Cantidad de OTs sin asignar acumuladas hasta ese día.
    asignada : int
        Cantidad de OTs asignadas no iniciadas.
    en_proceso : int
        Cantidad de OTs actualmente en trabajo.
    finalizado : int
        Cantidad de OTs cerradas ese día específico.
    """
    por_asignar: int
    asignada:    int
    en_proceso:  int
    finalizado:  int


class CalendarioSemanaResponse(BaseModel):
    """
    Respuesta de GET /calendario/semana.
    Conteos por día para los 7 días de la semana (lunes a domingo).

    Usado por WidgetCalendario.qml para pintar badges numéricos.

    Ejemplo:
    --------
    {
        "dias": {
            "2026-05-11": { "por_asignar": 1, "asignada": 0, "en_proceso": 2, "finalizado": 1 },
            ...
        }
    }
    """
    dias: dict[str, ResumenDia]


class CalendarioMesResponse(BaseModel):
    """
    Respuesta de GET /calendario/mes.
    Conteos por día para todos los días del mes.

    Usado por Calendario.qml para pintar cada celda del grid mensual.
    """
    dias: dict[str, ResumenDia]