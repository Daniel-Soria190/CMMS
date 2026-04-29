from pydantic import BaseModel, Field
from datetime import datetime 

class ManttoRequest (BaseModel):
    idOrden:int 
    tipo:str
    rPor:int
    externo:bool
    descripcion:str
    rPorExt:int

class ManttoResponse(BaseModel):
    idMantenimiento:int
    idOrden:int 
    tipo:str
    Fi:datetime
    Ff:datetime
    rPor:int
    vPor:int 
    externo:bool
    descripcion:str
    rPorExt:int