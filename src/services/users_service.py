from fastapi import HTTPException
from src.db.database import get_pool
#from src.models.users import UserRequest 


async def user_exists(user):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT 1 FROM public."Usuario"
            WHERE username = $1 OR email = $2;
            """,
            user.username,
            user.email,
        )
        
        print(row is not None )

        return row is not None 
    



async def set_user(user):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    

    if await user_exists(user):
        raise HTTPException(status_code=400, detail="El username o email ya estan registrados en la base de datos")

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