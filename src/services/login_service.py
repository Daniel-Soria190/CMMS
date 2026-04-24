from fastapi import HTTPException
from src.db.database import get_pool

async def user_exists(user):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")
       
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT username, email
            FROM public."Usuario"
            WHERE username= $1 or email = $2;
            """,
            user.username,
            user.email
        )
        print (row is not None)
        return row is not None


async def password_match(user):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")
       
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """   
            SELECT username, password_hash
            FROM public."Usuario"
            WHERE username = $1  and password_hash= $2
            """, 
        user.username,
        user.password_hash
        )
        print ( row is not None)
        return row is not None



def login():
    pass