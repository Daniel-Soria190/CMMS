from pydantic import BaseModel

class UserRequest(BaseModel):
    username:str
    email:str

class SaltResponse (BaseModel):
    password_salt:str

class LoginRequest (BaseModel):
    password_hashed:str

    