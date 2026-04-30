from src.services.websockets_service import manager
from asyncpg import Pool

async def crear_notificacion_y_notificar(pool: Pool, user_id: int, mensaje: str, tipo: str, data_incremental: dict = None):
    # 1. Persistir en PostgreSQL
    query = """
        INSERT INTO notificaciones (idUsuario, mensaje, tipo, fechaCreacion, leida)
        VALUES ($1, $2, $3, NOW(), FALSE)
        RETURNING idNotificacion;
    """
    async with pool.acquire() as conn:
        notif_id = await conn.fetchval(query, user_id, mensaje, tipo)

    # 2. Preparar el payload para el WebSocket
    payload = {
        "type": "NEW_NOTIFICATION",
        "idNotificacion": notif_id,
        "mensaje": mensaje,
        "tipo": tipo,
        "extra_data": data_incremental # Aquí van los cambios de las tablas
    }

    # 3. Enviar vía WebSocket en tiempo real
    await manager.send_personal_message(payload, user_id)