from fastapi import Query
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

class SearchResponse(BaseModel):
    marca: str
    modelo: str
    nombre: str
    numeroSerie: str
    area: str
    estado: str
    descripcion:str 


class SearchParams(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    nombre: Optional[str] = None
    numeroSerie: Optional[str] = None
    area: Optional[str] = None
    estado: Optional[str] = None

class InventarioResponse(BaseModel):
    numeroSerie: str
    estado: str
