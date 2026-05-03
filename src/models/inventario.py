from pydantic import BaseModel, Field
from datetime import date
from typing import Optional



class inventarioRequest (BaseModel):
    idEquipo:int
    numeroSerie:str
    estado:str =Field (default="Activo")
    fechaIngreso:date
    idArea:int
    garantia:bool
    expiracionGarantia:date
    idAdquisicion:int

class InventarioUpdate (BaseModel):
    idEquipo:Optional[int]=None
    numeroSerie:Optional[str]=None
    estado:Optional[str]=None
    idArea:Optional[int]=None
    garantia:Optional[bool]=None
    expiracionGarantia:Optional[date]=None  
    idAdquisicion:Optional[int]=None
    isDelete:Optional[bool]=None

class InventarioParams(BaseModel):
    idEquipo:Optional[int]=None
    numeroSerie:Optional[str]=None
    estado:Optional[str]=None
    fechaIngreso:Optional[date]=None
    idArea:Optional[int]=None
    garantia:Optional[bool]=None
    expiracionGarantia:Optional[date]=None


