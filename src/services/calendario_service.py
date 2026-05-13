from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException
from src.db.database import get_pool


# ── Queries ───────────────────────────────────────────────────────────────────

QUERY_POR_ASIGNAR = """
    SELECT
        ot."idOrden",
        ot."idEquipoInstalado",
        ot."folio",
        ot."descripcionFallo" AS falla,
        e."nombre",
        ei."numeroSerie"      AS "NoSerie",
        ei."ubicacion"        AS "Ubicacion"
    FROM public."OrdenTrabajo" ot
    JOIN public."EquipoInstalado" ei ON ei."idEquipoInstalado" = ot."idEquipoInstalado"
    JOIN public."Equipo"          e  ON e."idEquipo"           = ei."idEquipo"
    WHERE ot."estado" = 'por_asignar'
      AND ot."fechaSolicitud" <= $1
      {filtro_area}
    ORDER BY ot."fechaSolicitud"
"""

QUERY_ASIGNADA = """
    SELECT
        ot."idOrden",
        ot."idEquipoInstalado",
        ot."folio",
        ot."descripcionFallo" AS falla,
        e."nombre",
        ei."numeroSerie"      AS "NoSerie",
        ei."ubicacion"        AS "Ubicacion"
    FROM public."OrdenTrabajo" ot
    JOIN public."EquipoInstalado" ei ON ei."idEquipoInstalado" = ot."idEquipoInstalado"
    JOIN public."Equipo"          e  ON e."idEquipo"           = ei."idEquipo"
    WHERE ot."estado" = 'asignada'
      AND ot."fechaSolicitud" <= $1
      {filtro_area}
      {filtro_tecnico}
    ORDER BY ot."fechaSolicitud"
"""

QUERY_EN_PROCESO = """
    SELECT
        ot."idOrden",
        ot."idEquipoInstalado",
        m."idMantenimiento",
        ot."folio",
        e."nombre",
        ei."numeroSerie"      AS "NoSerie",
        ei."ubicacion"        AS "Ubicacion",
        u."nombre" || ' ' || COALESCE(u."apellido", '') AS tecnico
    FROM public."OrdenTrabajo" ot
    JOIN public."EquipoInstalado" ei ON ei."idEquipoInstalado" = ot."idEquipoInstalado"
    JOIN public."Equipo"          e  ON e."idEquipo"           = ei."idEquipo"
    JOIN public."Mantenimiento"   m  ON m."idOrden"            = ot."idOrden"
    LEFT JOIN public."Usuario"    u  ON u."idUsuario"          = ot."asignadoA"
    WHERE ot."estado" = 'en_proceso'
      {filtro_area}
      {filtro_tecnico}
    ORDER BY ot."fechaSolicitud"
"""

QUERY_FINALIZADO = """
    SELECT
        ot."idOrden",
        ot."idEquipoInstalado",
        m."idMantenimiento",
        ot."folio",
        e."nombre",
        ei."numeroSerie"       AS "NoSerie",
        ei."ubicacion"         AS "Ubicacion",
        m."descripcionTrabajo" AS nota,
        ot."fechaCierre"
    FROM public."OrdenTrabajo" ot
    JOIN public."EquipoInstalado" ei ON ei."idEquipoInstalado" = ot."idEquipoInstalado"
    JOIN public."Equipo"          e  ON e."idEquipo"           = ei."idEquipo"
    JOIN public."Mantenimiento"   m  ON m."idOrden"            = ot."idOrden"
    WHERE ot."estado" = 'finalizada'
      AND ot."fechaCierre" BETWEEN $1 AND $2
      {filtro_area}
      {filtro_tecnico}
    ORDER BY ot."fechaCierre"
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_filtros(id_rol: int, id_area: int | None, id_usuario: int) -> tuple[str, str]:
    """
    Construye fragmentos SQL de filtro según el rol del usuario.

    Parámetros:
    -----------
    id_rol : int
        1 = Administrador      → sin filtro
        2 = Encargado de Área  → filtra por idArea del equipo
        >= 3 = Técnico         → filtra por asignadoA = idUsuario

    id_area : int | None
        FK → Area.idArea. Requerido si idRol = 2.

    id_usuario : int
        FK → Usuario.idUsuario. Usado si idRol >= 3.

    Retorna:
    --------
    tuple[str, str] — (filtro_area, filtro_tecnico)
    """
    if id_rol == 1:
        return "", ""
    elif id_rol == 2:
        return f'AND ei."idArea" = {id_area}', ""
    else:
        return "", f'AND ot."asignadoA" = {id_usuario}'


def _to_dt(d: date, end_of_day: bool = False) -> datetime:
    """
    Convierte date a datetime con timezone UTC.

    Parámetros:
    -----------
    d : date
    end_of_day : bool
        Si True devuelve 23:59:59, si False devuelve 00:00:00.
    """
    if end_of_day:
        return datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)


async def _ejecutar_queries_dia(
    conn,
    fecha: date,
    filtro_area: str,
    filtro_tecnico: str,
    es_admin: bool,
) -> dict:
    """
    Ejecuta las cuatro queries para un día específico.

    Parámetros:
    -----------
    conn : asyncpg connection
    fecha : date
        Día consultado.
    filtro_area : str
        Fragmento SQL para filtrar por área. Vacío si no aplica.
    filtro_tecnico : str
        Fragmento SQL para filtrar por técnico. Vacío si no aplica.
    es_admin : bool
        Si False (técnico), por_asignar siempre retorna vacío.

    Retorna:
    --------
    dict con keys: por_asignar, asignada, en_proceso, finalizado
    """
    dt_tope = _to_dt(fecha, end_of_day=True)
    dt_inicio = _to_dt(fecha, end_of_day=False)

    # por_asignar — solo admin y encargado
    if es_admin:
        q = QUERY_POR_ASIGNAR.format(filtro_area=filtro_area)
        rows_por_asignar = await conn.fetch(q, dt_tope)
    else:
        rows_por_asignar = []

    # asignada
    q = QUERY_ASIGNADA.format(filtro_area=filtro_area, filtro_tecnico=filtro_tecnico)
    rows_asignada = await conn.fetch(q, dt_tope)

    # en_proceso
    q = QUERY_EN_PROCESO.format(filtro_area=filtro_area, filtro_tecnico=filtro_tecnico)
    rows_en_proceso = await conn.fetch(q)

    # finalizado — solo ese día
    q = QUERY_FINALIZADO.format(filtro_area=filtro_area, filtro_tecnico=filtro_tecnico)
    rows_finalizado = await conn.fetch(q, dt_inicio, dt_tope)

    return {
        "por_asignar": [dict(r) for r in rows_por_asignar],
        "asignada":    [dict(r) for r in rows_asignada],
        "en_proceso":  [dict(r) for r in rows_en_proceso],
        "finalizado":  [dict(r) for r in rows_finalizado],
    }


async def _ejecutar_queries_rango(
    conn,
    fecha_inicio: date,
    fecha_fin: date,
    filtro_area: str,
    filtro_tecnico: str,
    es_admin: bool,
) -> dict:
    """
    Ejecuta las queries para un rango de fechas — usado por semana y mes.
    Devuelve conteos en lugar de items completos.

    Retorna:
    --------
    dict {
        "por_asignar": int,
        "asignada": int,
        "en_proceso": int,
        "finalizado_por_dia": { "YYYY-MM-DD": int }
    }
    """
    dt_tope    = _to_dt(fecha_fin, end_of_day=True)
    dt_inicio  = _to_dt(fecha_inicio, end_of_day=False)

    if es_admin:
        q = QUERY_POR_ASIGNAR.format(filtro_area=filtro_area)
        count_por_asignar = len(await conn.fetch(q, dt_tope))
    else:
        count_por_asignar = 0

    q = QUERY_ASIGNADA.format(filtro_area=filtro_area, filtro_tecnico=filtro_tecnico)
    count_asignada = len(await conn.fetch(q, dt_tope))

    q = QUERY_EN_PROCESO.format(filtro_area=filtro_area, filtro_tecnico=filtro_tecnico)
    count_en_proceso = len(await conn.fetch(q))

    # Finalizado agrupado por día
    q = QUERY_FINALIZADO.format(filtro_area=filtro_area, filtro_tecnico=filtro_tecnico)
    rows_final = await conn.fetch(q, dt_inicio, dt_tope)

    finalizado_por_dia: dict[str, int] = {}
    for row in rows_final:
        if row["fechaCierre"]:
            dia_key = row["fechaCierre"].date().isoformat()
            finalizado_por_dia[dia_key] = finalizado_por_dia.get(dia_key, 0) + 1

    return {
        "por_asignar":       count_por_asignar,
        "asignada":          count_asignada,
        "en_proceso":        count_en_proceso,
        "finalizado_por_dia": finalizado_por_dia,
    }


def _construir_resumen_rango(
    datos: dict,
    fecha_inicio: date,
    fecha_fin: date,
) -> dict:
    """
    Construye el dict de resumen por día para semana y mes.

    Parámetros:
    -----------
    datos : dict
        Resultado de _ejecutar_queries_rango.
    fecha_inicio : date
    fecha_fin : date

    Retorna:
    --------
    dict { "YYYY-MM-DD": ResumenDia }
    por_asignar y asignada son iguales en todos los días del rango
    ya que son acumulados. finalizado varía por día.
    """
    resultado = {}
    delta = (fecha_fin - fecha_inicio).days + 1

    for i in range(delta):
        dia = (fecha_inicio + timedelta(days=i)).isoformat()
        resultado[dia] = {
            "por_asignar": datos["por_asignar"],
            "asignada":    datos["asignada"],
            "en_proceso":  datos["en_proceso"],
            "finalizado":  datos["finalizado_por_dia"].get(dia, 0),
        }

    return resultado


# ── Funciones públicas ────────────────────────────────────────────────────────

async def get_calendario_dia(
    fecha: date,
    id_rol: int,
    id_area: int | None,
    id_usuario: int,
) -> dict:
    """
    Detalle completo de órdenes para un día.
    Usado por el tablero diario / kanban.

    Retorna:
    --------
    CalendarioDiaResponse — por_asignar, asignada, en_proceso, finalizado
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    filtro_area, filtro_tecnico = _build_filtros(id_rol, id_area, id_usuario)
    es_admin = id_rol <= 2

    async with pool.acquire() as conn:
        return await _ejecutar_queries_dia(
            conn=conn,
            fecha=fecha,
            filtro_area=filtro_area,
            filtro_tecnico=filtro_tecnico,
            es_admin=es_admin,
        )


async def get_calendario_semana(
    fecha: date,
    id_rol: int,
    id_area: int | None,
    id_usuario: int,
) -> dict:
    """
    Conteos por día para la semana que contiene la fecha.
    Usado por WidgetCalendario.qml.

    Parámetros:
    -----------
    fecha : date
        Cualquier día de la semana. El sistema calcula lunes y domingo.
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    lunes   = fecha - timedelta(days=fecha.weekday())
    domingo = lunes + timedelta(days=6)

    filtro_area, filtro_tecnico = _build_filtros(id_rol, id_area, id_usuario)
    es_admin = id_rol <= 2

    async with pool.acquire() as conn:
        datos = await _ejecutar_queries_rango(
            conn=conn,
            fecha_inicio=lunes,
            fecha_fin=domingo,
            filtro_area=filtro_area,
            filtro_tecnico=filtro_tecnico,
            es_admin=es_admin,
        )

    return {"dias": _construir_resumen_rango(datos, lunes, domingo)}


async def get_calendario_mes(
    fecha: date,
    id_rol: int,
    id_area: int | None,
    id_usuario: int,
) -> dict:
    """
    Conteos por día para el mes completo.
    Usado por Calendario.qml.

    Parámetros:
    -----------
    fecha : date
        Cualquier día del mes. El sistema calcula primer y último día.
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    primer_dia = fecha.replace(day=1)
    if fecha.month == 12:
        ultimo_dia = fecha.replace(day=31)
    else:
        ultimo_dia = fecha.replace(month=fecha.month + 1, day=1) - timedelta(days=1)

    filtro_area, filtro_tecnico = _build_filtros(id_rol, id_area, id_usuario)
    es_admin = id_rol <= 2

    async with pool.acquire() as conn:
        datos = await _ejecutar_queries_rango(
            conn=conn,
            fecha_inicio=primer_dia,
            fecha_fin=ultimo_dia,
            filtro_area=filtro_area,
            filtro_tecnico=filtro_tecnico,
            es_admin=es_admin,
        )

    return {"dias": _construir_resumen_rango(datos, primer_dia, ultimo_dia)}