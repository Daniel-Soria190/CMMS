from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
# from fastapi.responses import Response
from src.services.websockets_service import manager
from src.services.auth_service import get_current_user_ws


router = APIRouter(prefix="/ws", tags=["websockets"])

# @router.websocket("/{user_id}")
# async def websocket_endpoint(websocket: WebSocket, user_id: int):
#     await manager.connect(user_id, websocket)
#     try:
#         while True:
#             # Mantener la conexión viva
#             data = await websocket.receive_text()
#             # Aquí podrías manejar mensajes entrantes si fuera necesario
#     except WebSocketDisconnect:
#         manager.disconnect(user_id, websocket)
#         print(f"Cliente {user_id} desconectado")
#     except Exception as e:
#         print(f"Error en socket: {e}")
#         manager.disconnect(user_id, websocket)

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    token = websocket.query_params.get("token")

    # 1. Validar token ANTES de aceptar
    if not token:
        await websocket.close(code=4001, reason="Token ausente")
        return

    user = await get_current_user_ws(token)

    if user is None:
        await websocket.close(code=4001, reason="Token inválido")
        return
    
    if user == "expirado":
        await websocket.close(code=401, reason="Token expirado")
        return

    # 2. Verificar rol
    ROL_MINIMO = 5  # Becario o superior
    if int(user["idRol"]) > ROL_MINIMO:
        await websocket.close(code=4003, reason="Acceso denegado")
        return

    # 3. Solo aceptar si todo está bien
    # await websocket.accept()
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
        print(f"Cliente {user_id} desconectado")
    except Exception as e:
        print(f"Error en socket: {e}")
        manager.disconnect(user_id, websocket)