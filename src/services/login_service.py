from fastapi import HTTPException
from src.db.database import get_pool

async def user_exists(q):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")
       
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT username
            FROM public."Usuario"
            WHERE username= $1 or email = $1;
            """,
            q
        )
        if not row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return row is not None, row["username"]


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

async def get_user(q):

    flag, username = await user_exists(q)

    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")
    
    if flag:
       
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT username, password_salt
                FROM public."Usuario"
                WHERE username= $1
                """,
                username
            )
        userdata = dict(row)
        return userdata

    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        

async def login(user):
    pass