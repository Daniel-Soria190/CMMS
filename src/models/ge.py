from pydantic import BaseModel, Field 
class funcionResponse(BaseModel):
    idFuncion:int
    categoria:str
    funcion:str
    peso:int

class riesgoResponse(BaseModel):
    idRiesgo:int
    descripcion:str
    peso:int

class ReqMtoResponse(BaseModel):
    idReqMto:int
    descripcion:str
    peso:int

class antecedenteResponse(BaseModel):
    idAntecedentes:int
    promedioAverias:str
    factor:int
