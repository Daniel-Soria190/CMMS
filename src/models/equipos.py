from pydantic import BaseModel, Field
from typing import Optional, Literal

class EquipoRequest(BaseModel):
    nombre:str
    marca:str 
    modelo:str
    descripcion:str
    tiempoVidaEstimado:str
    idFuncion:int
    idRiesgo:int
    idReqMto:int

class EquipoUpdate (BaseModel):
    nombre:Optional[str]= None
    marca:Optional[str]=None
    modelo:Optional[str]=None
    descripcion:Optional[str]=None
    tiempoVidaEstimado:Optional[str]=None
    idFuncion:Optional[int]=None
    idRiesgo:Optional[int]=None
    idReqMto:Optional[int]=None

class EquipoParams(BaseModel):
    nombre: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None

class EquipoResponse(BaseModel):
    idEquipo:int
    nombre:str
    marca:str 
    modelo:str
    tiempoVidaEstimado: int|str|None
    idFuncion: int|str|None
    idRiesgo: int|str|None
    idReqMto: int|str|None
