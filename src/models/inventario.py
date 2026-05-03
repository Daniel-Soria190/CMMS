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

class MattoUpdate (BaseModel):
    pass

class MattoParams(BaseModel):
    pass

