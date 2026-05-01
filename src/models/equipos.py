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
    idEquipo:int
    nombre:str
    marca:str 
    modelo:str
    descripcion:str
    t_vida:str
    idFuncion:int
    idRiesgo:int
    idReqMto:int