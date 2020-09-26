from typing import List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import json

app = FastAPI()


class WSConnectionManager:
    """
        params:     active_connection
        methods:    connect, disconnect, send_personal_message, broadcast
    """
    def __init__(self):
        self.active_connections: List[Dict[str, WebSocket]] = []

    async def connect(self, room: str, ws: WebSocket):
        await ws.accept()
        person_in_room = 0
        for connection in self.active_connections:
            if connection["room"] == room:
                person_in_room += 1
        await ws.send_text(str(person_in_room))
        self.active_connections.append({"room": room, "ws": ws})

    def disconnect(self, room: str, ws: WebSocket):
        self.active_connections.remove({"room": room, "ws": ws})

    @staticmethod
    async def send_personal_message(message: dict, ws: WebSocket):
        await ws.send_json(message)

    async def send_other_message(self, message: dict, room: str):
        for connection in self.active_connections:
            if connection["room"] == room:
                await connection['ws'].send_json(message)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection["ws"].send_json(data)


manager = WSConnectionManager()


@app.websocket("/ws/{room}")
async def websocket_endpoint(ws: WebSocket, room: str):
    await manager.connect(room, ws)
    try:
        while True:
            data = await ws.receive_text()
            data = json.loads(data)
            room = data["room"]
            if room:
                await manager.send_other_message(data, room)
    except WebSocketDisconnect:
        manager.disconnect(room, ws)

if __name__ == "__main__":
    import uvicorn
    # 官方推荐是用命令后启动 uvicorn main:app --host=127.0.0.1 --port=8010 --reload
    uvicorn.run(app='main:app', host="0.0.0.0", port=8010, reload=True, debug=True)





