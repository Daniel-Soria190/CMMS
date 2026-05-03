from fastapi import HTTPException
from src.db.database import get_pool,build_dynamic_query
from src.services.auth_service import generate_JWT, decode_JWT   
from datetime import datetime, timezone

#async def search (idOrden,idEquipoInstall,
#                  prioridad,estado,
#                  fechaSoli,fechaEnt,
#                  asignadoa,creadopor):
#    pool = await get_pool()
#    if pool is None:
#        raise HTTPException(status_code=500, detail="DB no inicializada") 
#
#    base_query = 'SELECT * FROM public."OrdenTrabajo"'
#    and_conditions = []
#    or_conditions = []
#   values = []
#
#    # AND (filtros)
#    if idOrden is not None:
#        and_conditions.append(f""" "idOrden" = ${len(values)+1}""")
#       values.append(idOrden)
#
#
#   if estado is not None:
#        and_conditions.append(f""" "estado" = ${len(values)+1}""")
#        values.append(estado)
#
#    if fechaSoli is not None:
#        and_conditions.append(f""" "fechaSolicitud" = ${len(values)+1}""")
#        values.append(fechaSoli)
#
#    if fechaEnt is not None:
#       and_conditions.append(f""" "fechaEntrega"= ${len(values)+1}""")
#        values.append(fechaEnt)
#
#    # OR (filtros alternativos)
#    if prioridad is not None:
#        or_conditions.append(f""" "prioridad" = ${len(values)+1}""")
#        values.append(prioridad)
#
#    if idEquipoInstall is not None:
#        or_conditions.append(f""" "idEquipoInstalado" = ${len(values)+1}""")
#        values.append(idEquipoInstall)
#
#    if asignadoa is not None:
#        or_conditions.append(f""" "asignadoA" = ${len(values)+1}""")
#        values.append(asignadoa)
#
#    if creadopor is not None:
#        or_conditions.append(f""" "creadoPorUsuario" = ${len(values)+1}""")
#        values.append(creadopor)
#
#    # Construir WHERE
#    if and_conditions or or_conditions:
#        base_query += " WHERE "
#
#        if and_conditions:
#           base_query += " AND ".join(and_conditions)
#
#        if or_conditions:
#            if and_conditions:
#                base_query += " AND "
#            base_query += "(" + " OR ".join(or_conditions) + ")"
#
#    rows = await pool.fetch(base_query, *values)
#
#    aux= [dict(row) for row in rows]
#
#    if aux:
#        return aux
#    else:
#        return HTTPException(status_code=404, detail="orden no encontrada") 
#=======================================================================================================


async def search(params: dict, limit: int = 10, offset: int = 0):
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    # 1. Definir columnas permitidas
    WHITELIST = [ "idEquipoInstalado" ,"prioridad" ,
                 "estado" ,"fechaSolicitud" , 
                 "FechaEntrega" ,"asignadoA" , 
                 "creadoPorUsuario" ]
    
    print(params)
    # 2. Construir WHERE dinámico
    where_str, values = build_dynamic_query(params, WHITELIST)
    print(where_str)
    print(values)
    # 3. Construir query final con paginación
    # Importante: El LIMIT y OFFSET también usan placeholders por seguridad
    sql = f"""
        SELECT * FROM public."OrdenTrabajo"
        {where_str}
        ORDER BY "idOrden"  -- Recomendado para que la paginación sea consistente
        LIMIT ${len(values) + 1} OFFSET ${len(values) + 2}
    """
    
    # Añadimos los valores de paginación a la lista de argumentos
    full_values = [*values, limit, offset]

    rows = await pool.fetch(sql, *full_values)
    
    if not rows:
        # Nota: Es mejor devolver lista vacía [] que un 404 en búsquedas, 
        # pero mantengo tu lógica si así lo prefieres.
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")

    return [dict(row) for row in rows]

#======================================================================================================

async def get_orden(idOrden):
    pool = await get_pool()

    if pool is None:
       raise HTTPException(status_code=500, detail="DB no inicializada") 
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT * FROM public."OrdenTrabajo"
            WHERE "idOrden" =$1;
            """,
            idOrden,     
        )
        if row == None:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        return dict(row)

#=======================================================================================================0



#======================================================================================================0




#========================================================================================================
async def set_orden(orden):
    pool = await get_pool()

    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada") 
    #if await equipo_exists(equipo):
     #   raise HTTPException(status_code=400, detail="Este modelo ya existe en la base de datos")
    now= datetime.now(timezone.utc)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO public."OrdenTrabajo"(
            "idEquipoInstalado", 
            "descripcionFallo", prioridad, 
            estado, "fechaSolicitud", 
            "asignadoA", "creadoPorUsuario", 
            "creadoPorExterno")
	
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
            """,
            orden.idEquipoInstall,
            orden.descripcion,
            orden.prioridad,
            orden.estado,
            now,
            orden.asignadoa,
            orden.creadopor,
            orden.creadoporext
        )
        return {"status": "Orden de mantenimiento generada con exito."}