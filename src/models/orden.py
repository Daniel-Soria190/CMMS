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