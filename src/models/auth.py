from pydantic import BaseModel

class SaltRequest(BaseModel):
    username: str

class LoginRequest(BaseModel):
    username: str
    password_hash: str

class TokenResponse (BaseModel):
    token:str 
    