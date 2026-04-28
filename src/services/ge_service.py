from fastapi import HTTPException
from src.db.database import get_pool
from src.services.auth_service import generate_JWT, decode_JWT

async def get_funcion ():
    pool= await get_pool()
    
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        
        rows = await conn.fetch(
           """
            SELECT "idFuncion", categoria, funcion, peso
	        FROM public."GEFuncion";
            """     
        )
        
        funciondata= [dict(row) for row in rows]
        return funciondata
    
async def get_riesgo ():
    pool= await get_pool()
    
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        
        rows = await conn.fetch(
           """
            SELECT "idRiesgo", descripcion, peso
	        FROM public."GERiesgo";
            """     
        )
        
        Riesgodata= [dict(row) for row in rows]
        return Riesgodata

async def get_ReqMto ():
    pool= await get_pool()
    
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        
        rows = await conn.fetch(
           """
            SELECT "idReqMto", descripcion, peso
	        FROM public."GEMantenimiento";
            """     
        )
        
        ReqMtodata= [dict(row) for row in rows]
        return ReqMtodata


async def get_antecedentes ():
    pool= await get_pool()
    
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        
        rows = await conn.fetch(
           """
            SELECT "idAntecedentes", "promedioAverias", factor
	        FROM public."GEAntecedentes";
            """     
        )
        
        antecedentesdata= [dict(row) for row in rows]
        return antecedentesdata
    