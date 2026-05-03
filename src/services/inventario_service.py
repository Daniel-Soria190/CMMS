from fastapi import HTTPException
from src.db.database import get_pool, build_dynamic_query
from src.services.auth_service import generate_JWT, decode_JWT   
#========================================================================



async def inventario_exists(invent):
    pool = await get_pool()

   # if pool is None:
    #    raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT 1 FROM public."EquipoInstalado"
            WHERE "numeroSerie"=$1;
            """,
            invent.numeroSerie,     
        )
        
        print(row is not None )

        return row is not None


#===========================================================================
async def set_inventario(invent):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    

    if await inventario_exists(invent):
        raise HTTPException(status_code=400, detail="Este equipo ya existe en la base de datos")

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO public."EquipoInstalado"(
            "idEquipo",
            "numeroSerie",
            estado,
            "fechaIngreso",
            "idArea",
            garantia,
            "expiracionGarantia",
            "idAdquisicion")
	
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
            """,
           invent.idEquipo,
           invent.numeroSerie,
           invent.estado,
           invent.fechaIngreso,
           invent.idArea,
           invent.garantia,
           invent.expiracionGarantia,
           invent.idAdquisicion
        )
        return {"status": "Equipo agregado con exito."}