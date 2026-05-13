from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException
from src.db.database import get_pool


# ── Query base ────────────────────────────────────────────────────────────────

QUERY_PENDIENTES = """
    SELECT
        ot."idOrden",
        ot."idEquipoInstalado",
        ot."folio",
        ot."descripcionFallo"   AS falla,
        e."nombre",
        ei."numeroSerie"        AS "NoSerie",
        ei."ubicacion"          AS "Ubicacion"
    FROM public."OrdenTrabajo" ot
    JOIN public."EquipoInstalado" ei ON ei."idEquipoInstalado" = ot."idEquipoInstalado"
    JOIN public."Equipo"          e  ON e."idEquipo"           = ei."idEquipo"
    WHERE ot."estado" IN ('por_asignar', 'asignada')
      AND ot."fechaSolicitud" <= $1
      {filtro_area}
      {filtro_tecnico}
    ORDER BY ot."fechaSolicitud"
"""

QUERY_MANTENIMIENTO = """
    SELECT
        ot."idOrden",
        ot."idEquipoInstalado",
        m."idMantenimiento",
        ot."folio",
        e."nombre",
        ei."numeroSerie"        AS "NoSerie",
        ei."ubicacion"          AS "Ubicacion",
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
        ei."numeroSerie"        AS "NoSerie",
        ei."ubicacion"          AS "Ubicacion",
        m."descripcionTrabajo"  AS nota,
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



def _build_filtros(id_rol: int, id_area: int | None, id_usuario: int) -> tuple[str, str]:
    """
    Construye los fragmentos SQL de filtro según el rol del usuario.

    Parámetros:
    -----------
    id_rol : int
        Rol del usuario autenticado.
        1 = Administrador → sin filtro
        2 = Encargado de Área → filtra por idArea del equipo instalado
        >= 3 = Técnico/Ingeniero → filtra por asignadoA = idUsuario

    id_area : int | None
        FK → Area.idArea del usuario.
        Requerido si idRol = 2.

    id_usuario : int
        FK → Usuario.idUsuario del usuario autenticado.
        Usado si idRol >= 3.

    Retorna:
    --------
    tuple[str, str] — (filtro_area, filtro_tecnico)
    Fragmentos SQL listos para interpolar en las queries base.
    """
    if id_rol == 1:
        return "", ""
    elif id_rol == 2:
        return f'AND ei."idArea" = {id_area}', ""
    else:
        return "", f'AND ot."asignadoA" = {id_usuario}'


async def _ejecutar_queries(
    conn,
    fecha_inicio: date,
    fecha_fin: date,
    filtro_area: str,
    filtro_tecnico: str,
) -> dict:

    # Convertir date a datetime con timezone para que asyncpg infiera el tipo
    dt_inicio = datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day, 
                         0, 0, 0, tzinfo=timezone.utc)
    dt_fin    = datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day, 
                         23, 59, 59, tzinfo=timezone.utc)

    # Pendientes
    q_pend = QUERY_PENDIENTES.format(
        filtro_area=filtro_area,
        filtro_tecnico=filtro_tecnico,
    )
    rows_pend = await conn.fetch(q_pend, dt_fin)

    # En proceso
    q_mant = QUERY_MANTENIMIENTO.format(
        filtro_area=filtro_area,
        filtro_tecnico=filtro_tecnico,
    )
    rows_mant = await conn.fetch(q_mant)

    # Finalizadas
    q_final = QUERY_FINALIZADO.format(
        filtro_area=filtro_area,
        filtro_tecnico=filtro_tecnico,
    )
    rows_final = await conn.fetch(q_final, dt_inicio, dt_fin)

    return {
        "pendientes":    [dict(r) for r in rows_pend],
        "mantenimiento": [dict(r) for r in rows_mant],
        "finalizado":    [dict(r) for r in rows_final],
    }


# ── Endpoints de servicio ─────────────────────────────────────────────────────

async def get_calendario_dia(
    fecha: date,
    id_rol: int,
    id_area: int | None,
    id_usuario: int,
) -> dict:
    """
    Obtiene las órdenes de trabajo para un día específico.

    Parámetros:
    -----------
    fecha : date
        Día consultado. Formato: YYYY-MM-DD
    id_rol : int
        FK → Rol.idRol del usuario autenticado.
    id_area : int | None
        FK → Area.idArea. Requerido si idRol = 2.
    id_usuario : int
        FK → Usuario.idUsuario del usuario autenticado.

    Retorna:
    --------
    CalendarioDiaResponse — pendientes, mantenimiento, finalizado del día.
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    filtro_area, filtro_tecnico = _build_filtros(id_rol, id_area, id_usuario)

    async with pool.acquire() as conn:
        return await _ejecutar_queries(
            conn=conn,
            fecha_inicio=fecha,
            fecha_fin=fecha,
            filtro_area=filtro_area,
            filtro_tecnico=filtro_tecnico,
        )


async def get_calendario_semana(
    fecha: date,
    id_rol: int,
    id_area: int | None,
    id_usuario: int,
) -> dict:
    """
    Obtiene las órdenes agrupadas por día para la semana que contiene la fecha.

    Parámetros:
    -----------
    fecha : date
        Cualquier día de la semana consultada.
        El sistema calcula el lunes y domingo de esa semana.
    id_rol / id_area / id_usuario : ver get_calendario_dia.

    Retorna:
    --------
    dict { "dias": { "YYYY-MM-DD": CalendarioDiaResponse, ... } }
    Siempre devuelve los 7 días de la semana, con listas vacías si no hay datos.
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    # Calcular lunes y domingo de la semana
    lunes  = fecha - timedelta(days=fecha.weekday())
    domingo = lunes + timedelta(days=6)

    filtro_area, filtro_tecnico = _build_filtros(id_rol, id_area, id_usuario)

    async with pool.acquire() as conn:
        datos = await _ejecutar_queries(
            conn=conn,
            fecha_inicio=lunes,
            fecha_fin=domingo,
            filtro_area=filtro_area,
            filtro_tecnico=filtro_tecnico,
        )

    return {"dias": _agrupar_por_dia(datos, lunes, domingo)}


async def get_calendario_mes(
    fecha: date,
    id_rol: int,
    id_area: int | None,
    id_usuario: int,
) -> dict:
    """
    Obtiene las órdenes agrupadas por día para el mes completo.

    Parámetros:
    -----------
    fecha : date
        Cualquier día del mes consultado.
        El sistema calcula el primer y último día del mes.
    id_rol / id_area / id_usuario : ver get_calendario_dia.

    Retorna:
    --------
    dict { "dias": { "YYYY-MM-DD": CalendarioDiaResponse, ... } }
    Devuelve todos los días del mes, con listas vacías si no hay datos.
    """
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    # Primer y último día del mes
    primer_dia = fecha.replace(day=1)
    if fecha.month == 12:
        ultimo_dia = fecha.replace(day=31)
    else:
        ultimo_dia = fecha.replace(month=fecha.month + 1, day=1) - timedelta(days=1)

    filtro_area, filtro_tecnico = _build_filtros(id_rol, id_area, id_usuario)

    async with pool.acquire() as conn:
        datos = await _ejecutar_queries(
            conn=conn,
            fecha_inicio=primer_dia,
            fecha_fin=ultimo_dia,
            filtro_area=filtro_area,
            filtro_tecnico=filtro_tecnico,
        )

    return {"dias": _agrupar_por_dia(datos, primer_dia, ultimo_dia)}


def _agrupar_por_dia(datos: dict, fecha_inicio: date, fecha_fin: date) -> dict:
    """
    Agrupa los items del calendario por día dentro de un rango.

    Parámetros:
    -----------
    datos : dict
        Resultado de _ejecutar_queries con keys pendientes, mantenimiento, finalizado.
    fecha_inicio : date
        Primer día del rango.
    fecha_fin : date
        Último día del rango.

    Retorna:
    --------
    dict { "YYYY-MM-DD": { pendientes, mantenimiento, finalizado } }

    Nota:
    -----
    - pendientes y mantenimiento aparecen en todos los días del rango
      ya que no tienen fecha específica dentro del periodo.
    - finalizado se agrupa por su fechaCierre::date.
    """
    resultado = {}
    delta = (fecha_fin - fecha_inicio).days + 1

    # Inicializar todos los días del rango con listas vacías
    for i in range(delta):
        dia = fecha_inicio + timedelta(days=i)
        resultado[dia.isoformat()] = {
            "pendientes":    [],
            "mantenimiento": [],
            "finalizado":    [],
        }

    # pendientes y mantenimiento van en todos los días del rango
    for item in datos["pendientes"]:
        for dia_key in resultado:
            resultado[dia_key]["pendientes"].append(item)

    for item in datos["mantenimiento"]:
        for dia_key in resultado:
            resultado[dia_key]["mantenimiento"].append(item)

    # finalizado se agrupa por fechaCierre
    for item in datos["finalizado"]:
        if "fechaCierre" in item and item["fechaCierre"]:
            dia_key = item["fechaCierre"].date().isoformat()
            if dia_key in resultado:
                resultado[dia_key]["finalizado"].append(item)

    return resultado