from fastapi import APIRouter, HTTPException
from src.db.database import pool
from src.models.auth import SaltRequest, LoginRequest
import secrets
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/salt")
async def get_salt(data: SaltRequest):

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT password_salt, activo
            FROM "Usuario"
            WHERE username = $1
            """,
            data.username
        )

    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not row["activo"]:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    return {"salt": row["password_salt"]}

SESSION_DURATION_MINUTES = 30

@router.post("/login")
async def login(data: LoginRequest):

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    async with pool.acquire() as conn:

        user = await conn.fetchrow(
            """
            SELECT "idUsuario", password_hash, activo
            FROM "Usuario"
            WHERE username = $1
            """,
            data.username
        )

        # return {"message": "Hello World"}   
    

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if not user["activo"]:
            raise HTTPException(status_code=403, detail="Usuario inactivo")

        # validación de hash (ya viene del cliente)
        if user["password_hash"] != data.password_hash:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        # generar token
        token = secrets.token_urlsafe(32)

        now = datetime.utcnow()
        expires = now + timedelta(minutes=SESSION_DURATION_MINUTES)

        await conn.execute(
            """
            INSERT INTO "Sesion"
            ("idUsuario", "token", "fechaCreacion", "ultimaActividad", "expiraEn", "activa")
            VALUES ($1, $2, $3, $3, $4, TRUE)
            """,
            user["idUsuario"],
            token,
            now,
            expires
        )

    return {
        "token": token,
        "expires": expires.isoformat()
    }