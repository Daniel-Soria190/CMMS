from pydantic import BaseModel

class UserRequest(BaseModel):
    name:str
    lastname:str 
    username: str
    email:str
    password_hash:str
    password_salt:str
    idArea:int
    idRol:int


