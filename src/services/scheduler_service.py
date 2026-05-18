from datetime import date, datetime, timezone
from fastapi import HTTPException
from src.db.database import get_pool


# ── Constantes ────────────────────────────────────────────────────────────────

USUARIO_SISTEMA = 0  # FK → Usuario.idUsuario del usuario sistema


# ── Función principal del scheduler ──────────────────────────────────────────

async def ejecutar_revision_planes():
    """
    Revisión periódica de planes de mantenimiento.
    Se ejecuta al arrancar el servidor y cada 8 horas.

    Flujo:
    ------
    1. Obtiene todos los equipos con numeroGE >= 12 desde VistaEquipoGE
    2. Para cada equipo busca sus planes activos en PlanMantenimiento
    3. Si la proximaEjecucion (o override) <= hoy y no hay orden generada:
       - Crea OrdenTrabajo con tipoOrden = plan.tipo
       - Actualiza ultimaEjecucion, proximaEjecucion y idOrdenGenerada
       - Limpia proximaEjecucionOverride si fue usada
    """
    pool = await get_pool()
    if pool is None:
        print("[SCHEDULER] Pool no disponible, omitiendo revisión.")
        return

    hoy = date.today()
    print(f"[SCHEDULER] Iniciando revisión — {hoy}")

    async with pool.acquire() as conn:

        # ── 1. Equipos con GE >= 12 ───────────────────────────────────────
        equipos = await conn.fetch(
            """
            SELECT "idEquipoInstalado", "numeroGE", "frecuencia_dias"
            FROM public."VistaEquipoGE"
            WHERE "numeroGE" >= 12
            """
        )

        if not equipos:
            print("[SCHEDULER] No hay equipos con GE >= 12.")
            return

        print(f"[SCHEDULER] Equipos elegibles: {len(equipos)}")

        for equipo in equipos:
            id_ei         = equipo["idEquipoInstalado"]
            frecuencia_ge = equipo["frecuencia_dias"]

            # ── 2. Planes activos del equipo ──────────────────────────────
            planes = await conn.fetch(
                """
                SELECT *
                FROM public."PlanMantenimiento"
                WHERE "idEquipoInstalado" = $1
                  AND "activo" = true
                """,
                id_ei,
            )

            for plan in planes:
                await _procesar_plan(conn, plan, hoy, frecuencia_ge)

    print(f"[SCHEDULER] Revisión completada — {hoy}")


async def _procesar_plan(conn, plan: dict, hoy: date, frecuencia_ge: int):
    """
    Evalúa un plan individual y genera OrdenTrabajo si corresponde.

    Parámetros:
    -----------
    conn : asyncpg connection
    plan : dict
        Fila de PlanMantenimiento
    hoy : date
    frecuencia_ge : int
        frecuencia_dias calculada por VistaEquipoGE para este equipo.
        Solo se usa si plan.frecuenciaAuto = True.
    """
    id_plan    = plan["idPlan"]
    id_ei      = plan["idEquipoInstalado"]
    tipo       = plan["tipo"]
    auto       = plan["frecuenciaAuto"]
    override   = plan["proximaEjecucionOverride"]
    proxima    = plan["proximaEjecucion"]
    orden_gen  = plan["idOrdenGenerada"]

    # Determinar la fecha efectiva a evaluar
    fecha_efectiva = override if override is not None else proxima

    if fecha_efectiva is None:
        print(f"[SCHEDULER] Plan {id_plan} sin fecha de ejecución, omitiendo.")
        return

    if fecha_efectiva > hoy:
        print(f"[SCHEDULER] Plan {id_plan} próxima ejecución {fecha_efectiva}, no es hoy.")
        return

    # Verificar que no haya una orden ya generada pendiente
    if orden_gen is not None:
        orden_abierta = await conn.fetchval(
            """
            SELECT 1 FROM public."OrdenTrabajo"
            WHERE "idOrden" = $1
              AND "estado" NOT IN ('finalizada', 'cancelada')
            """,
            orden_gen,
        )
        if orden_abierta:
            print(f"[SCHEDULER] Plan {id_plan} ya tiene orden {orden_gen} abierta, omitiendo.")
            return

    # ── 3. Crear OrdenTrabajo ─────────────────────────────────────────────
    now = datetime.now(timezone.utc)

    id_orden = await conn.fetchval(
        """
        INSERT INTO public."OrdenTrabajo"(
            "idEquipoInstalado",
            "descripcionFallo",
            "prioridad",
            "estado",
            "fechaSolicitud",
            "creadoPorUsuario",
            "tipoOrden"
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING "idOrden"
        """,
        id_ei,
        f"Mantenimiento {'preventivo' if tipo == 'preventiva' else 'de inspección'} programado automáticamente.",
        "media",
        "por_asignar",
        now,
        USUARIO_SISTEMA,
        tipo,
    )

    # Generar folio
    folio = f"OT-{now.year}-{id_orden:05d}"
    await conn.execute(
        'UPDATE public."OrdenTrabajo" SET "folio" = $1 WHERE "idOrden" = $2',
        folio,
        id_orden,
    )

    # ── 4. Calcular nueva proximaEjecucion ────────────────────────────────
    frecuencia = frecuencia_ge if auto else plan["frecuenciaDias"]

    from datetime import timedelta
    nueva_proxima = hoy + timedelta(days=frecuencia)

    # ── 5. Actualizar PlanMantenimiento ───────────────────────────────────
    await conn.execute(
        """
        UPDATE public."PlanMantenimiento"
        SET "ultimaEjecucion"          = $1,
            "proximaEjecucion"         = $2,
            "proximaEjecucionOverride" = NULL,
            "idOrdenGenerada"          = $3,
            "frecuenciaDias"           = $4
        WHERE "idPlan" = $5
        """,
        hoy,
        nueva_proxima,
        id_orden,
        frecuencia,
        id_plan,
    )

    print(f"[SCHEDULER] Plan {id_plan} → Orden {folio} creada. Próxima: {nueva_proxima}")


# ── Gestión de planes ─────────────────────────────────────────────────────────

async def crear_plan(data: dict, id_usuario: int) -> dict:
    """
    Crea un plan de mantenimiento inicial para un equipo.
    Solo el administrador puede llamar esto.

    Parámetros:
    -----------
    data : dict
        Campos de PlanCreate
    id_usuario : int
        FK → Usuario.idUsuario del admin que crea el plan.

    Validaciones:
    -------------
    - idEquipoInstalado debe existir
    - tipo debe ser 'preventiva' o 'inspeccion'
    - Si frecuenciaAuto = False, frecuenciaDias es obligatorio
    - No puede haber ya un plan activo del mismo tipo para el mismo equipo
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    if data["tipo"] not in ("preventiva", "inspeccion"):
        raise HTTPException(status_code=422, detail="tipo debe ser 'preventiva' o 'inspeccion'")

    if not data["frecuenciaAuto"] and not data.get("frecuenciaDias"):
        raise HTTPException(
            status_code=422,
            detail="frecuenciaDias es obligatorio cuando frecuenciaAuto = False",
        )

    async with pool.acquire() as conn:

        # Verificar que el equipo existe y tiene GE >= 12
        equipo = await conn.fetchrow(
            """
            SELECT "idEquipoInstalado", "numeroGE", "frecuencia_dias"
            FROM public."VistaEquipoGE"
            WHERE "idEquipoInstalado" = $1
            """,
            data["idEquipoInstalado"],
        )
        if equipo is None:
            raise HTTPException(status_code=404, detail="Equipo instalado no encontrado.")

        if equipo["numeroGE"] < 12:
            raise HTTPException(
                status_code=422,
                detail=f"El equipo tiene GE={equipo['numeroGE']}. Solo se programan equipos con GE >= 12.",
            )

        # Verificar que no exista ya un plan activo del mismo tipo
        existente = await conn.fetchval(
            """
            SELECT 1 FROM public."PlanMantenimiento"
            WHERE "idEquipoInstalado" = $1
              AND "tipo" = $2
              AND "activo" = true
            """,
            data["idEquipoInstalado"],
            data["tipo"],
        )
        if existente:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un plan activo de tipo '{data['tipo']}' para este equipo.",
            )

        # Calcular frecuencia
        frecuencia = equipo["frecuencia_dias"] if data["frecuenciaAuto"] else data["frecuenciaDias"]

        # Insertar plan
        row = await conn.fetchrow(
            """
            INSERT INTO public."PlanMantenimiento"(
                "idEquipoInstalado",
                "tipo",
                "frecuenciaDias",
                "proximaEjecucion",
                "activo",
                "frecuenciaAuto",
                "creadoPor",
                "fechaCreacion"
            )
            VALUES ($1, $2, $3, $4, true, $5, $6, NOW())
            RETURNING *
            """,
            data["idEquipoInstalado"],
            data["tipo"],
            frecuencia,
            data["fechaInicio"],
            data["frecuenciaAuto"],
            id_usuario,
        )

        return dict(row)


async def listar_planes(activo: bool | None = None) -> list[dict]:
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    async with pool.acquire() as conn:
        if activo is not None:
            rows = await conn.fetch(
                'SELECT * FROM public."PlanMantenimiento" WHERE "activo" = $1 ORDER BY "idPlan"',
                activo,
            )
        else:
            rows = await conn.fetch(
                'SELECT * FROM public."PlanMantenimiento" ORDER BY "idPlan"'
            )
        return [dict(r) for r in rows]


async def get_plan(id_plan: int) -> dict:
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT * FROM public."PlanMantenimiento" WHERE "idPlan" = $1',
            id_plan,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Plan no encontrado.")
        return dict(row)


async def actualizar_plan(id_plan: int, data: dict) -> dict:
    """
    Actualiza campos permitidos de un plan.
    Usado para sobreescribir fechas o pausar el plan.
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    if not data:
        raise HTTPException(status_code=400, detail="Nada para actualizar.")

    async with pool.acquire() as conn:
        existente = await conn.fetchval(
            'SELECT 1 FROM public."PlanMantenimiento" WHERE "idPlan" = $1',
            id_plan,
        )
        if existente is None:
            raise HTTPException(status_code=404, detail="Plan no encontrado.")

        campos = ", ".join([f'"{k}" = ${i+1}' for i, k in enumerate(data.keys())])
        valores = list(data.values())
        valores.append(id_plan)

        await conn.execute(
            f'UPDATE public."PlanMantenimiento" SET {campos} WHERE "idPlan" = ${len(valores)}',
            *valores,
        )

        row = await conn.fetchrow(
            'SELECT * FROM public."PlanMantenimiento" WHERE "idPlan" = $1',
            id_plan,
        )
        return dict(row)