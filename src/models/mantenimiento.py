from pydantic import BaseModel, Field
from datetime import datetime 
from typing import Optional
from fastapi import Query 


class ManttoRequest (BaseModel):
    idOrden:int 
    tipo:str
    rPor:int
    externo:bool
    descripcion:str
    rPorExt:int






