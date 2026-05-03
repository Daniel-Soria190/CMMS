from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    name:str
    lastname:str 
    username: str
    email:str
    password_hash:str
    password_salt:str
    idArea:int
    idRol:int

class userUpdate(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    username:Optional[str]=None
    email:Optional[str]=None
    password_hash:Optional[str]=None
    idArea:Optional[int]=None
    activo:Optional[bool]=None
    idRol:Optional[int]=None
    isDeleted:Optional[bool]=None

class userParams(BaseModel):

    nombre: Optional[str] = None
    apellido: Optional[str] = None
    username:Optional[str]=None
    email:Optional[str]=None 
    idArea:Optional[int]=None
    activo:Optional[bool]=None
    idRol:Optional[int]=None
    isDeleted:Optional[bool]=None
