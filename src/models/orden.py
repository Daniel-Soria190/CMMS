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


