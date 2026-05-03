from pydantic import BaseModel, Field
from datetime import datetime 
from typing import Optional



class MattoRequest (BaseModel):
    idOrden:int 
    tipo:str
    rPor:int
    externo:bool
    descripcion:str
    rPorExt:int
class MattoUpdate (BaseModel):
    idOrden: Optional[int]= None
    tipo: Optional[str]=None
    fechaInicio: Optional[datetime]=None
    fechaFin: Optional[datetime]=None
    realizadoPor: Optional[int]=None
    verificadoPor: Optional[int]=None
    externo: Optional[bool]=None
    descripcionTrabajo: Optional [str]=None
    realizadoPorExterno: Optional[int]=None


class MattoParams(BaseModel):
    idOrden: Optional[int]= None
    tipo: Optional[str]=None
    fechaInicio: Optional[datetime]=None
    fechaFin: Optional[datetime]=None
    realizadoPor: Optional[int]=None
    verificadoPor: Optional[int]=None
    externo: Optional[bool]=None
    realizadoPorExterno: Optional[int]=None


