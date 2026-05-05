from fastapi import HTTPException
from src.db.database import get_pool,build_dynamic_query
from src.services.auth_service import generate_JWT, decode_JWT  



async def search(params: dict, limit: int = 10, offset: int = 0):
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    # 1. Definir columnas permitidas
    WHITELIST = [  "nombre" ,  "apellido" , 
                  "username" , "email" ,
                  "idArea" , "activo" ,
                  "idRol" , "isDeleted" ]
    

    # 2. Construir WHERE dinámico
    where_str, values = build_dynamic_query(params, WHITELIST)

    # 3. Construir query final con paginación
    # Importante: El LIMIT y OFFSET también usan placeholders por seguridad
    sql = f"""
        SELECT * FROM public."Usuario"
        {where_str}
        ORDER BY "idUsuario"  -- Recomendado para que la paginación sea consistente
        LIMIT ${len(values) + 1} OFFSET ${len(values) + 2}
    """
    
    # Añadimos los valores de paginación a la lista de argumentos
    full_values = [*values, limit, offset]

    rows = await pool.fetch(sql, *full_values)
    
    if not rows:
        # Nota: Es mejor devolver lista vacía [] que un 404 en búsquedas, 
        # pero mantengo tu lógica si así lo prefieres.
        raise HTTPException(status_code=404, detail= "Usuario no encontrado")

    return [dict(row) for row in rows]
#=======================================================================================


async def get_user(idUser):
    pool = await get_pool()

    if pool is None:
       raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT * FROM public."Usuario"
            WHERE "idUsuario" =$1;
            """,
            idUser,     
        )
        if row == None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return dict(row)
#=================================================================================================


async def update(id, data:dict):
    pool= await get_pool()

    if pool is None:
       raise HTTPException(status_code=500, detail="DB no inicializada") 

    if await get_user(id): #devuelve vacio o bien se puede agregar un error 404

       

       # data = {
       #     k: v for k, v in aux.items()
       #     if v not in ("string", "", None, 0)
       # }
        
        if not data:
            raise HTTPException(status_code=400, detail="Nada para actualizar")
        
        update_data = ", ".join(
        [f'"{k}" = ${i+1}' for i, k in enumerate(data.keys())]
        )
        query = f'UPDATE public."Usuario" SET {update_data} WHERE "idUsuario" = ${len(data)+1}'

        values = list(data.values())
        values.append(id)

        async with pool.acquire() as conn:
                await conn.execute(
                query,*values
                )
                return {"staus": "Usuario actualizado con exito"}


#==================================================================================================00
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