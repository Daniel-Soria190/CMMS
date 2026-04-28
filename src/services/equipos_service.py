from fastapi import HTTPException
from src.db.database import get_pool
from src.services.auth_service import generate_JWT, decode_JWT   


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