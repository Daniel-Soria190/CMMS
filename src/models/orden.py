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


class CalendarioItem(BaseModel):
    """
    Representa una orden de trabajo en el calendario.

    Campos:
    -------
    idOrden : int
        PK → OrdenTrabajo.idOrden
    idEquipoInstalado : int
        FK → EquipoInstalado.idEquipoInstalado
    idMantenimiento : Optional[int]
        FK → Mantenimiento.idMantenimiento
        Solo presente en categorías 'mantenimiento' y 'finalizado'.
    folio : str
        Identificador legible. Formato: OT-YYYY-NNNNN
    nombre : str
        Nombre del equipo. FK → Equipo.nombre
    NoSerie : str
        Número de serie de la instancia física.
        UK → EquipoInstalado.numeroSerie
    Ubicacion : str
        Ubicación física del equipo instalado.
    falla : Optional[str]
        Descripción del fallo. Solo en categoría 'pendientes'.
    tecnico : Optional[str]
        Nombre completo del técnico asignado. Solo en 'mantenimiento'.
        FK → Usuario.idUsuario via OrdenTrabajo.asignadoA
    nota : Optional[str]
        Descripción del trabajo realizado. Solo en 'finalizado'.
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
    Respuesta de GET /calendario/dia y cada día en /semana y /mes.

    Campos:
    -------
    pendientes : list[CalendarioItem]
        OTs con estado 'por_asignar' o 'asignada'
        cuya fechaSolicitud <= fecha consultada.
        Incluye órdenes atrasadas de días anteriores.
    mantenimiento : list[CalendarioItem]
        OTs con estado 'en_proceso' sin restricción de fecha.
    finalizado : list[CalendarioItem]
        OTs con estado 'finalizada' cuya fechaCierre
        cae dentro del periodo consultado.
    """
    pendientes:    list[CalendarioItem]
    mantenimiento: list[CalendarioItem]
    finalizado:    list[CalendarioItem]


class CalendarioSemanaResponse(BaseModel):
    """
    Respuesta de GET /calendario/semana.
    Objeto con clave YYYY-MM-DD por cada día de la semana.

    Ejemplo:
    --------
    {
        "2026-05-11": { "pendientes": [], "mantenimiento": [], "finalizado": [] },
        "2026-05-12": { ... },
        ...
    }
    """
    dias: dict[str, CalendarioDiaResponse]


class CalendarioMesResponse(BaseModel):
    """
    Respuesta de GET /calendario/mes.
    Objeto con clave YYYY-MM-DD por cada día del mes.
    Usado por el widget Calendario.qml para pintar cada celda.
    """
    dias: dict[str, CalendarioDiaResponse]