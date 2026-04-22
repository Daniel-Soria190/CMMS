from fastapi import HTTPException
from src.db.database import get_pool
#from src.models.users import UserRequest 

async def set_user(user):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO public."Usuario"(
            nombre, 
            apellido, 
            username, 
            email, 
            password_hash, 
            password_salt, 
            "idArea",  
            "idRol")
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
            """,
            user.name,
            user.lastname,
            user.username,
            user.email,
            user.password_hash, 
            user.password_salt, 
            user.idArea, 
            user.idRol
        )
        return {"status": "Usuario agregado con exito."}