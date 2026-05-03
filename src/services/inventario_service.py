from fastapi import HTTPException
from src.db.database import get_pool, build_dynamic_query
from src.services.auth_service import generate_JWT, decode_JWT   


#========================================================================



async def search(params: dict, limit: int = 10, offset: int = 0):
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    # 1. Definir columnas permitidas
    WHITELIST = [  "idEquipo" ,  "numeroSerie" , 
                  "estado" , "fechaIngreso" ,
                  "idArea" , "garantia" ,
                  "expiracionGarantia" ]
    

    # 2. Construir WHERE dinámico
    where_str, values = build_dynamic_query(params, WHITELIST)

    # 3. Construir query final con paginación
    # Importante: El LIMIT y OFFSET también usan placeholders por seguridad
    sql = f"""
        SELECT * FROM public."EquipoInstalado"
        {where_str}
        ORDER BY "idEquipoInstalado"  -- Recomendado para que la paginación sea consistente
        LIMIT ${len(values) + 1} OFFSET ${len(values) + 2}
    """
    
    # Añadimos los valores de paginación a la lista de argumentos
    full_values = [*values, limit, offset]

    rows = await pool.fetch(sql, *full_values)
    
    if not rows:
        # Nota: Es mejor devolver lista vacía [] que un 404 en búsquedas, 
        # pero mantengo tu lógica si así lo prefieres.
        raise HTTPException(status_code=404, detail= "Equipo no encontrado")

    return [dict(row) for row in rows]

#=======================================================================


async def get_invent(idInventario):
    pool = await get_pool()

    if pool is None:
       raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT * FROM public."EquipoInstalado"
            WHERE "idEquipoInstalado" =$1;
            """,
            idInventario,     
        )
        if row == None:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")

        return dict(row)

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