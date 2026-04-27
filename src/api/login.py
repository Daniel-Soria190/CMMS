from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.login import UserRequest, LoginRequest, SaltResponse
from src.services.login_service import user_exists, password_match, get_user

router = APIRouter(prefix="/login", tags=["login"])

@router.get("/user/", response_model=SaltResponse,
            summary="Buscar usuario",
            description="Busca un usuario por username o email en la BD",
            response_description="username, password_salt"
            )
async def user(q: str):
  """
  Busca un usuario por username o email

  Parametros:
  -----------
  q: str;
  Parametro de busqueda (email o correo)
  """
  return await get_user(q)


@router.post("/login")
async def login(login_password:LoginRequest):
    return await password_match(login_password)