from fastapi import HTTPException
from src.db.database import get_pool
from src.services.auth_service import generate_JWT, decode_JWT   


async def search (nombre, marca, modelo):
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 

    base_query = 'SELECT * FROM public."Equipo"'
    filters = []
    values = []

    # Construcción dinámica
    if nombre:
        filters.append(f"nombre ILIKE ${len(values)+1}")
        values.append(f"%{nombre}%")

    if marca:
        filters.append(f"marca ILIKE ${len(values)+1}")
        values.append(f"%{marca}%")

    if modelo:
        filters.append(f"modelo ILIKE ${len(values)+1}")
        values.append(f"%{modelo}%")

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    rows = await pool.fetch(base_query, *values)

    aux= [dict(row) for row in rows]

    if aux:
        return aux
    else:
        return HTTPException(status_code=404, detail="equipo no encontrado") 

    #return [dict(row) for row in rows]






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