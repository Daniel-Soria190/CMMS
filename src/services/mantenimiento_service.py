from fastapi import HTTPException
from src.db.database import get_pool
from src.services.auth_service import generate_JWT, decode_JWT   
from datetime import datetime ,timezone


async def search (idOrden,tipo,
                  Fi,Ff,rPor,
                  vPor,externo,
                  rPorExt):
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 

    base_query = 'SELECT * FROM public."Mantenimiento"'
    and_conditions = []
    or_conditions = []
    values = []

    if idOrden is not None:
        and_conditions.append(f""" "idOrden" = ${len(values)+1}""")
        values.append(idOrden)

    if tipo is not None:
        and_conditions.append(f"tipo = ${len(values)+1}")
        values.append(tipo)

    if Fi is not None:
        and_conditions.append(f""" "fechaInicio" >= ${len(values)+1}""")
        values.append(Fi)

    if Ff is not None:
        and_conditions.append(f""" "fechaFin" <= ${len(values)+1}""")
        values.append(Ff)

    # 🔹 OR (flexibles)
    if rPor is not None:
        or_conditions.append(f""" "realizadoPor" = ${len(values)+1}""")
        values.append(rPor)

    if vPor is not None:
        or_conditions.append(f""" "verificadoPor" = ${len(values)+1}""")
        values.append(vPor)

    if externo is not None:
        or_conditions.append(f"externo = ${len(values)+1}")
        values.append(externo)

    if rPorExt is not None:
        or_conditions.append(f""" "realizadoPorExterno" = ${len(values)+1}""")
        values.append(rPorExt)

    # 🔹 Construcción final
    if and_conditions or or_conditions:
        base_query += " WHERE "

        if and_conditions:
            base_query += " AND ".join(and_conditions)

        if or_conditions:
            if and_conditions:
                base_query += " AND "
            base_query += "(" + " OR ".join(or_conditions) + ")"


    rows = await pool.fetch(base_query, *values)

    aux= [dict(row) for row in rows]

    if aux:
        return aux
    else:
        return HTTPException(status_code=404, detail="orden no encontrada") 


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