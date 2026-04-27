from fastapi import HTTPException
# from src.db.database import get_pool
from datetime import datetime, timedelta,timezone
from jose import jwt, JWTError, ExpiredSignatureError
from src.core.config import *

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
        return payload
    except ExpiredSignatureError:
        return "Token expirado"
    except JWTError:
        return "Token inválido"

def refresh_JWT():
    pass

def expires_JWT():
    pass
