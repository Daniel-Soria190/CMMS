from fastapi import HTTPException
from src.db.database import get_pool,build_dynamic_query
from src.services.auth_service import generate_JWT, decode_JWT   
from datetime import datetime, timezone
from src.services.notificaciones_service import crear_notificacion_y_notificar

import os
import uuid
import aiofiles
from fastapi import UploadFile

UPLOAD_DIR = "media/ordenes"
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

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

async def id_exist(id):
    pool = await get_pool()

   # if pool is None:
    #    raise HTTPException(status_code=500, detail="DB no inicializada")   
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
           """
            SELECT 1 FROM public."OrdenTrabajo"
            WHERE "idOrden"=$1;
            """,
            id   
        )

        return row is not None 

#======================================================================================================0

async def update(id, data:dict):
    pool= await get_pool()

    if pool is None:
       raise HTTPException(status_code=500, detail="DB no inicializada") 

    if await id_exist(id): #devuelve vacion o bien se puede agregar un error 404

       # aux= Orden.dict()

      #  data = {
      #      k: v for k, v in aux.items()
        #    if v not in ("string", "", None, 0)
       # }
        
        if not data:
            raise HTTPException(status_code=400, detail="Nada para actualizar")
        
        update_data = ", ".join(
        [f'"{k}" = ${i+1}' for i, k in enumerate(data.keys())]
        )
        query = f'UPDATE public."OrdenTrabajo" SET {update_data} WHERE "idOrden" = ${len(data)+1}'

        values = list(data.values())
        values.append(id)

        async with pool.acquire() as conn:
                await conn.execute(
                query,*values
                )
                return {"staus": "Orden de trabajo actualizada con exito"}

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
    
# ── Al final del archivo, reemplaza la versión anterior de crear_reporte_orden ──


async def crear_reporte_orden(
    id_equipo_instalado: int,
    descripcion_fallo: str,
    prioridad: str,
    id_usuario: int | None,
    contacto: dict | None,
) -> dict:
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    if id_usuario is None and contacto is None:
        raise HTTPException(
            status_code=422,
            detail="Debe proporcionar datos de contacto o iniciar sesión.",
        )

    async with pool.acquire() as conn:

        # ── 1. Resolver origen ────────────────────────────────────────────────
        id_creado_por_usuario    = None
        id_creado_por_reportante = None

        if id_usuario is not None:
            id_creado_por_usuario = id_usuario
        else:
            id_creado_por_reportante = await _resolver_reportante(conn, contacto)

        # ── 2. Insertar OrdenTrabajo ──────────────────────────────────────────
        now = datetime.now(timezone.utc)
        row = await conn.fetchrow(
            """
            INSERT INTO public."OrdenTrabajo"(
                "idEquipoInstalado",
                "descripcionFallo",
                "prioridad",
                "estado",
                "fechaSolicitud",
                "creadoPorUsuario",
                "creadoPorReportante"
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING "idOrden", "fechaSolicitud"
            """,
            id_equipo_instalado,
            descripcion_fallo.strip(),
            prioridad,
            "por_asignar",
            now,
            id_creado_por_usuario,
            id_creado_por_reportante,
        )
        id_orden = row["idOrden"]
        fecha_solicitud = row["fechaSolicitud"]

        # ── 3. Generar y guardar folio ────────────────────────────────────────
        folio = f"OT-{now.year}-{id_orden:05d}"
        await conn.execute(
            'UPDATE public."OrdenTrabajo" SET "folio" = $1 WHERE "idOrden" = $2',
            folio,
            id_orden,
        )

    # ── 4. Notificar admins ───────────────────────────────────────────────────
    await _notificar_admins_nueva_orden(pool, id_orden, folio, descripcion_fallo, prioridad)

    return {
        "idOrden":              id_orden,
        "folio":                folio,
        "estado":               "por_asignar",
        "fechaSolicitud":       fecha_solicitud,
        "idEquipoInstalado":    id_equipo_instalado,
        "creadoPorUsuario":     id_creado_por_usuario,
        "creadoPorReportante":  id_creado_por_reportante,
        "archivosSubidos":      0,
        "mensaje":              f"Orden {folio} creada correctamente.",
    }


async def _resolver_reportante(conn, contacto: dict) -> int:
    correo = contacto.get("correo")

    if correo:
        existente = await conn.fetchval(
            'SELECT "idReportante" FROM public."Reportante" WHERE "correo" = $1',
            correo,
        )
        if existente:
            return existente

    row = await conn.fetchrow(
        """
        INSERT INTO public."Reportante"("nombre", "telefono", "correo")
        VALUES ($1, $2, $3)
        RETURNING "idReportante"
        """,
        contacto["nombre"],
        contacto.get("telefono"),
        correo,
    )
    return row["idReportante"]


async def _notificar_admins_nueva_orden(
    pool, id_orden: int, folio: str, descripcion: str, prioridad: str
):
    """
    Obtiene todos los admins activos y llama al servicio de notificaciones
    por cada uno. Fallo aquí no revierte la OT.
    """
    try:
        async with pool.acquire() as conn:
            admins = await conn.fetch(
                """
                SELECT "idUsuario" FROM public."Usuario"
                WHERE "idRol" = 1
                  AND "activo" = true
                  AND "isDeleted" = false
                """,
            )

        for admin in admins:
            await crear_notificacion_y_notificar(
                pool=pool,
                user_id=admin["idUsuario"],
                mensaje=f"Nueva orden {folio} — {descripcion[:80]}",
                tipo="nueva_orden",
                data_incremental={
                    "evento":      "nueva_orden",
                    "folio":       folio,
                    "idOrden":     id_orden,
                    "prioridad":   prioridad,
                    "descripcion": descripcion[:120],
                },
            )
    except Exception as e:
        print(f"[WARN] Notificación fallida para nueva orden {folio}: {e}")


# ==================================================================================

async def asignar_orden(id_orden: int, id_asignado: int) -> dict:
    """
    Asigna un técnico a una orden de trabajo y crea el registro de Mantenimiento.

    Parámetros:
    -----------
    id_orden : int
        PK de OrdenTrabajo. Debe existir y estar en estado 'por_asignar'.
        FK → OrdenTrabajo.idOrden
    id_asignado : int
        PK del usuario técnico.
        FK → Usuario.idUsuario

    Operaciones:
    ------------
    1. Valida que la OT existe y su estado es 'por_asignar'.
       Check: estado IN ('por_asignar','asignada','en_proceso','finalizada','cancelada')
    2. Valida que el usuario existe en la tabla Usuario.
    3. Actualiza OrdenTrabajo:
       - asignadoA = id_asignado
       - estado    = 'asignada'
    4. Crea registro en Mantenimiento:
       - idOrden      = id_orden
       - tipo         = tipoOrden de la OT (correctiva | preventiva | inspeccion)
       - realizadoPor = id_asignado
       - externo      = false
       - fechaInicio  = NULL (el técnico la llena al iniciar)
    5. Notifica al técnico por WS usando crear_notificacion_y_notificar.

    Retorna:
    --------
    dict con idOrden, idMantenimiento, folio, estado, asignadoA, mensaje.

    Errores:
    --------
    404 — OT no encontrada.
    409 — OT no está en estado 'por_asignar'.
    404 — Usuario asignado no encontrado.
    500 — DB no inicializada.
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    async with pool.acquire() as conn:

        # ── 1. Verificar que la OT existe y está en estado correcto ──────────
        orden = await conn.fetchrow(
            """
            SELECT "idOrden", "folio", "estado", "tipoOrden"
            FROM public."OrdenTrabajo"
            WHERE "idOrden" = $1
            """,
            id_orden,
        )
        if orden is None:
            raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada.")

        if orden["estado"] != "por_asignar":
            raise HTTPException(
                status_code=409,
                detail=f"La orden no puede asignarse porque está en estado '{orden['estado']}'.",
            )

        # ── 2. Verificar que el usuario existe ───────────────────────────────
        usuario = await conn.fetchval(
            """
            SELECT "idUsuario" FROM public."Usuario"
            WHERE "idUsuario" = $1
            """,
            id_asignado,
        )
        if usuario is None:
            raise HTTPException(status_code=404, detail="El usuario asignado no existe.")

        # ── 3. Actualizar OrdenTrabajo ────────────────────────────────────────
        await conn.execute(
            """
            UPDATE public."OrdenTrabajo"
            SET "asignadoA" = $1,
                "estado"    = 'asignada'
            WHERE "idOrden" = $2
            """,
            id_asignado,
            id_orden,
        )

        # ── 4. Crear registro en Mantenimiento ────────────────────────────────
        id_mantenimiento = await conn.fetchval(
            """
            INSERT INTO public."Mantenimiento"(
                "idOrden",
                "tipo",
                "realizadoPor",
                "externo"
            )
            VALUES ($1, $2, $3, false)
            RETURNING "idMantenimiento"
            """,
            id_orden,
            orden["tipoOrden"],
            id_asignado,
        )

    # ── 5. Notificar al técnico por WS ────────────────────────────────────────
    await _notificar_tecnico_asignado(
        pool=pool,
        id_usuario=id_asignado,
        id_orden=id_orden,
        folio=orden["folio"],
    )

    return {
        "idOrden":         id_orden,
        "idMantenimiento": id_mantenimiento,
        "folio":           orden["folio"],
        "estado":          "asignada",
        "asignadoA":       id_asignado,
        "mensaje":         f"Orden {orden['folio']} asignada correctamente.",
    }


async def _notificar_tecnico_asignado(
    pool, id_usuario: int, id_orden: int, folio: str
):
    """
    Persiste notificación en DB y envía WS al técnico asignado.

    Parámetros:
    -----------
    pool : asyncpg.Pool
    id_usuario : int
        FK → Usuario.idUsuario del técnico a notificar.
    id_orden : int
        FK → OrdenTrabajo.idOrden de referencia.
    folio : str
        Folio legible de la OT para el mensaje.

    Nota:
    -----
    Fallo en esta función no revierte la asignación — se captura
    silenciosamente para no afectar la respuesta principal.
    """
    try:
        await crear_notificacion_y_notificar(
            pool=pool,
            user_id=id_usuario,
            mensaje=f"Se te ha asignado la orden {folio}.",
            tipo="orden_asignada",
            data_incremental={
                "evento":  "orden_asignada",
                "folio":   folio,
                "idOrden": id_orden,
            },
        )
    except Exception as e:
        print(f"[WARN] Notificación WS fallida para técnico {id_usuario}: {e}")