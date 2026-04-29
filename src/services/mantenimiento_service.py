from fastapi import HTTPException
from src.db.database import get_pool
from src.services.auth_service import generate_JWT, decode_JWT   
from datetime import datetime ,timezone

async def mantto_exists(mantto):
    pool = await get_pool()

   # if pool is None:
    #    raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT 1 FROM public."Mantenimiento"
            WHERE "idOrden"=$1;
            """,
            mantto.idOrden   
        )
        
        print(row is not None )

        return row is not None 
    

async def set_mantto(mantto):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    

    if await mantto_exists(mantto):
        raise HTTPException(status_code=400, detail="Este equipo ya se encuentra en mantenimiento")

    now= datetime.now(timezone.utc)
  
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO public."Mantenimiento"(
            "idOrden",
            tipo, 
            "fechaInicio", 
            "realizadoPor", 
            externo, 
            "descripcionTrabajo",
            "realizadoPorExterno")
	        VALUES ($1, $2, $3, $4, $5, $6, $7);
            """,
            mantto.idOrden, 
            mantto.tipo, 
            now,
            mantto.rPor, 
            mantto.externo, 
            mantto.descripcion, 
            mantto.rPorExt
        )
        return {"status": "Mantenimiento agregado con exito."}