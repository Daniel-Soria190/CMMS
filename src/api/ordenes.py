from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.users import UserRequest
from src.services.users_service import set_user
from src.services.websockets_service import manager

router = APIRouter(prefix="/ordenes", tags=["ordenes"])


@router.post("/test-notificacion/{user_id}")
async def enviar_notificacion_prueba(user_id: int, mensaje: str = "Nueva actualización de equipo"):
    """
    Endpoint para probar que el WebSocket recibe datos 
    cuando ocurre un evento HTTP POST.
    """
    # 1. Simulamos el cambio incremental que mencionaste
    payload = {
        "event": "TABLA_ACTUALIZADA",
        "tabla": "equipoInstalado",
        "data": {
            "idEquipoInstalado": 101,
            "nuevo_estado": "Mantenimiento",
            "mensaje": mensaje
        }
    }

    # 2. Usamos el manager para enviar el mensaje al usuario específico
    # Si el usuario está conectado en el WS, recibirá esto instantáneamente
    await manager.send_personal_message(payload, user_id)

    return {
        "status": "Notificación enviada vía WS", 
        "usuario_objetivo": user_id,
        "data_enviada": payload
    }