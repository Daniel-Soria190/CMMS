from fastapi import HTTPException
from src.db.database import get_pool, build_dynamic_query
from src.services.auth_service import generate_JWT, decode_JWT   
from datetime import datetime ,timezone


async def search(params: dict, limit: int = 10, offset: int = 0):
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    # 1. Definir columnas permitidas
    WHITELIST = [""" "idOrden" """,  "tipo", 
                 """ "fechaInicio" """,""" "fechaFin" """,
                 """ "realizadoPor" """,""" "verificadoPor" """,
                 "externo" ,""" "realizadoPorExterno" """]

    # 2. Construir WHERE dinámico
    where_str, values = build_dynamic_query(params, WHITELIST)

    # 3. Construir query final con paginación
    # Importante: El LIMIT y OFFSET también usan placeholders por seguridad
    sql = f"""
        SELECT * FROM public."Mantenimiento"
        {where_str}
        ORDER BY "idMantenimiento"  -- Recomendado para que la paginación sea consistente
        LIMIT ${len(values) + 1} OFFSET ${len(values) + 2}
    """
    
    # Añadimos los valores de paginación a la lista de argumentos
    full_values = [*values, limit, offset]

    rows = await pool.fetch(sql, *full_values)
    
    if not rows:
        # Nota: Es mejor devolver lista vacía [] que un 404 en búsquedas, 
        # pero mantengo tu lógica si así lo prefieres.
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    return [dict(row) for row in rows]




#Revisar si es necesario identificar si ya existe un mantenimiento por medio 
#del idOrden, sino se puede simplemente quitar la funcion.
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
        
        #print(row is not None )

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