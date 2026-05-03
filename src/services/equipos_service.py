from fastapi import HTTPException
from src.db.database import get_pool, build_dynamic_query
from src.services.auth_service import generate_JWT, decode_JWT   

async def search(params: dict, limit: int = 10, offset: int = 0):
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")
 
    # 1. Definir columnas permitidas
    WHITELIST = ["nombre", "marca", "modelo"]

    # 2. Construir WHERE dinámico
    where_str, values = build_dynamic_query(params, WHITELIST)

    # 3. Construir query final con paginación
    # Importante: El LIMIT y OFFSET también usan placeholders por seguridad
    sql = f"""
        SELECT * FROM public."Equipo"
        {where_str}
        ORDER BY "idEquipo"  -- Recomendado para que la paginación sea consistente
        LIMIT ${len(values) + 1} OFFSET ${len(values) + 2}
    """
    
    # Añadimos los valores de paginación a la lista de argumentos
    full_values = [*values, limit, offset]

    rows = await pool.fetch(sql, *full_values)
    
    if not rows:
        # Nota: Es mejor devolver lista vacía [] que un 404 en búsquedas, 
        # pero mantengo tu lógica si así lo prefieres.
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    return [dict(row) for row in rows]

# async def search (nombre, marca, modelo):
#     pool = await get_pool()
#     if pool is None:
#         raise HTTPException(status_code=500, detail="DB no inicializada") 

#     base_query = 'SELECT * FROM public."Equipo"'
#     filters = []
#     values = []

#     # Construcción dinámica
#     if nombre:
#         filters.append(f"nombre ILIKE ${len(values)+1}")
#         values.append(f"%{nombre}%")

#     if marca:
#         filters.append(f"marca ILIKE ${len(values)+1}")
#         values.append(f"%{marca}%")

#     if modelo:
#         filters.append(f"modelo ILIKE ${len(values)+1}")
#         values.append(f"%{modelo}%")

#     if filters:
#         base_query += " WHERE " + " AND ".join(filters)

#     rows = await pool.fetch(base_query, *values)

#     aux= [dict(row) for row in rows]

#     if aux:
#         return aux
#     else:
#         return HTTPException(status_code=404, detail="Equipo no encontrado") 

#     #return [dict(row) for row in rows]


async def update(id, equipo):
    pool= await get_pool()

    if pool is None:
       raise HTTPException(status_code=500, detail="DB no inicializada") 


    aux= equipo.dict()

    data = {
        k: v for k, v in aux.items()
        if v not in ("string", "", None, 0)
    }
    
    if not data:
        raise HTTPException(status_code=400, detail="Nada para actualizar")
    

    
    update_data = ", ".join(
    [f'"{k}" = ${i+1}' for i, k in enumerate(data.keys())]
    )
    query = f'UPDATE public."Equipo" SET {update_data} WHERE "idEquipo" = ${len(data)+1}'

    values = list(data.values())
    values.append(id)

    async with pool.acquire() as conn:
            await conn.execute(
            query,*values
            )
            return {"staus": "Equipo actualizado con exito"}



async def equipo_exists(equipo):
    pool = await get_pool()

   # if pool is None:
    #    raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT 1 FROM public."Equipo"
            WHERE modelo=$1;
            """,
            equipo.modelo,     
        )
        
        print(row is not None )

        return row is not None 
    
async def get_Equipo(idEquipo):
    pool = await get_pool()

    if pool is None:
       raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT * FROM public."Equipo"
            WHERE "idEquipo" =$1;
            """,
            idEquipo,     
        )
        if row == None:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")

        return dict(row)

async def set_equipo(equipo):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    

    if await equipo_exists(equipo):
        raise HTTPException(status_code=400, detail="Este modelo ya existe en la base de datos")

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO public."Equipo"(
	        nombre, 
            marca, 
            modelo,
            descripcion, 
            "tiempoVidaEstimado", 
            "idFuncion", 
            "idRiesgo", 
            "idReqMto")
	
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
            """,
            equipo.nombre, 
            equipo.marca, 
            equipo.modelo,
            equipo.descripcion, 
            equipo.t_vida, 
            equipo.idFuncion, 
            equipo.idRiesgo, 
            equipo.idReqMto
        )
        return {"status": "Equipo agregado con exito."}