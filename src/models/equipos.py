from pydantic import BaseModel, Field
from typing import Optional, Literal

class EquipoRequest(BaseModel):
    nombre:str
    marca:str 
    modelo:str
    descripcion:str
    t_vida:str
    idFuncion:int
    idRiesgo:int
    idReqMto:int

class EquipoUpdate (BaseModel):
    nombre:Optional[str]= Field(default=None)
    marca:Optional[str]=Field(default=None)
    modelo:Optional[str]=Field(default=None)
    descripcion:Optional[str]=Field(default=None)
    tiempoVidaEstimado:Optional[str]=Field(default=None)
    idFuncion:Optional[int]=Field(default=None)
    idRiesgo:Optional[int]=Field(default=None)
    idReqMto:Optional[int]=Field(default=None)