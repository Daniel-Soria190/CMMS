from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    username:str
    email:str

class SaltResponse (BaseModel):
    idUsuario: int = Field(description="ID de usuario")
    password_salt:str = Field(description="Salt de la contraseña")

class LoginRequest (BaseModel):
    idUsuario: int
    password_hash:str

    