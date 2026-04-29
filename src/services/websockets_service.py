from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Mapeo de idUsuario -> Lista de WebSockets (por si tiene varias pestañas abiertas)
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Envía un mensaje JSON a un usuario específico"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    async def broadcast(self, message: dict):
        """Envía un mensaje a todos los conectados (útil para cambios en catálogos generales)"""
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                await connection.send_json(message)

# Instancia única para ser importada en otros servicios
manager = ConnectionManager()