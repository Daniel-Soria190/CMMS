from fastapi import Depends, HTTPException, status, Request
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.db.database import get_pool
from datetime import datetime, timedelta,timezone
from jose import jwt, JWTError, ExpiredSignatureError
from src.core.config import *

bearer_scheme = HTTPBearer()

def generate_JWT(payload, minutes=EXPIRAEN):
    """
    Genera un token nuevo dado un payload en base a las variables de entorno

    Parametros:
    -----------

    payload: dict

    Returns:
    --------
    token: str
    """
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=float(minutes))
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

    return token

def decode_JWT(token:str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        print(payload)
        return payload
    except ExpiredSignatureError:
        return "Token expirado"
    except JWTError:
        return "Token inválido"

def refresh_JWT(token):
    payload = decode_JWT(token)
    new_token = generate_JWT(payload)
    return {"token": new_token}
    

def expires_JWT():
    pass

async def get_idRol(id_usuario):
    """
    Obtiene el rol y área del usuario para incluir en el payload del JWT.

    Parámetros:
    -----------
    id_usuario : int
        FK → Usuario.idUsuario

    Retorna:
    --------
    dict con idRol, rol (nombre), idArea
    """
    pool = await get_pool()

    row = await pool.fetchrow(
        """
        SELECT 
            "Usuario"."idRol",
            "Usuario"."idArea",
            "Rol"."nombre" AS rol
        FROM "Usuario"
        JOIN "Rol" ON "Rol"."idRol" = "Usuario"."idRol"
        WHERE "Usuario"."idUsuario" = $1
        """,
        id_usuario,
    )

    return row



async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Valida el JWT y retorna los datos del usuario actual.

    Retorna:
    --------
    dict con idUsuario, idRol, idArea, rol (nombre del rol)

    Errores:
    --------
    401 — Token inválido, expirado o usuario no encontrado.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        id_usuario: int = payload.get("idUsuario")
        if id_usuario is None:
            raise ValueError("idUsuario ausente en el token")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token caducado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    row = await get_idRol(id_usuario)

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return {
        "idUsuario": id_usuario,
        "idRol":     row["idRol"],
        "idArea":    row["idArea"],
        "rol":       row["rol"],
    }

def require_role(id_rol_minimo: int):
    """
    id_rol_minimo: el idRol máximo permitido (inclusive).
    1: "Administrador",
    2: "Encargado de Area",
    3: "Ingeniero",
    4: "Técnico",
    5: "Becario",
    6: "Invitado",
    7: "Alex"
    """
    async def dependency(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        if current_user["idRol"] > id_rol_minimo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere el rol '{_nombre_rol(id_rol_minimo)}' o superior",
            )
        return current_user
    return dependency


def _nombre_rol(id_rol: int) -> str:
    nombres = {
        1: "Administrador",
        2: "Encargado de Area",
        3: "Ingeniero",
        4: "Técnico",
        5: "Becario",
        6: "Invitado",
        7: "Alex"
    }
    return nombres.get(id_rol, str(id_rol))

# auth_service.py
async def get_current_user_ws(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        id_usuario: int = payload.get("idUsuario")
        if id_usuario is None:
            return None
    except ExpiredSignatureError:
        return "expirado"   # distingue expirado de inválido
    except JWTError:
        return None

    row = await get_idRol(id_usuario)
    
    return dict(row) if row else None

async def get_usuario_opcional(
    request: Request,
) -> Optional[int]:
    """
    Extrae idUsuario del JWT si viene en Authorization: Bearer <token>.
    No lanza error si no hay token — retorna None.
    Úsalo como Depends() en endpoints públicos con trazabilidad opcional.
    """
    from fastapi import Request  # ya importado en el contexto de FastAPI
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        id_usuario = payload.get("idUsuario")
        if id_usuario is None:
            return None
        return int(id_usuario)
    except (JWTError, ExpiredSignatureError):
        return None