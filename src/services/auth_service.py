from fastapi import Depends, HTTPException, status
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

def refresh_JWT():
    pass

def expires_JWT():
    pass


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    pool = await get_pool()

    # 1. Decodificar JWT
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

    # 2. Buscar usuario y su rol en la BD
    row = await pool.fetchrow(
        """
        SELECT "Usuario"."idRol", "Rol".Nombre AS rol
        FROM "Usuario" "Usuario"
        JOIN "Rol" "Rol" ON "Rol"."idRol" = "Usuario"."idRol"
        WHERE "Usuario"."idUsuario" = $1
        """,
        id_usuario,
    )

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    # Retorna: {'idRol': 2, 'rol': 'Encargado de Area'}
    return dict(row)

def require_role(id_rol_minimo: int):
    """
    id_rol_minimo: el idRol máximo permitido (inclusive).
    Ej: require_role(3) permite Administrador(1), Encargado(2) e Ingeniero(3).
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