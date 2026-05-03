from pydantic import BaseModel
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