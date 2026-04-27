from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    username:str
    email:str

class SaltResponse (BaseModel):
    username: str = Field(description="Nombre de usuario")
    password_salt:str = Field(description="Salt de la contraseña")

class LoginRequest (BaseModel):
    username:str
    password_hash:str

    