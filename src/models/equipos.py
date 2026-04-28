from pydantic import BaseModel, Field

class equipoRequest(BaseModel):
    nombre:str
    marca:str 
    modelo:str
    descripcion:str
    t_vida:str
    idFuncion:int
    idRiesgo:int
    idReqMto:int

