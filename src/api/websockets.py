from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
# from fastapi.responses import Response
from src.services.websockets_service import manager


router = APIRouter(prefix="/ws", tags=["websockets"])

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Mantener la conexión viva
            data = await websocket.receive_text()
            # Aquí podrías manejar mensajes entrantes si fuera necesario
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
        print(f"Cliente {user_id} desconectado")
    except Exception as e:
        print(f"Error en socket: {e}")
        manager.disconnect(user_id, websocket)