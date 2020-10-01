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


def ai_process(state):
    import pickle
    import numpy as np
    import random
    import copy

    state = copy.deepcopy(state)
    character_list = state["character_list"]
    blacks = []
    whites = []
    for index_1 in range(3):
        for index_2 in range(3):
            index = index_1*3 + index_2
            if character_list[index_1][index_2]["type"] == 0:
                blacks.append(index)
            elif character_list[index_1][index_2]["type"] == 1:
                whites.append(index)
    character = {"white": whites, "black": blacks}
    f = open('Q.data', 'rb')
    obj = pickle.load(f)
    environment = obj["environment"]
    q_matrix = np.mat(obj["q_matrix"])
    state_index = 0
    for environment_item in environment:
        if environment_item["white"] == character["white"] and environment_item["black"] == character["black"]:
            break
        else:
            state_index += 1
    q_list = q_matrix[state_index]
    q_list = q_list.tolist()
    q_list = q_list[0]
    max_q = max(q_list)
    next_states = []
    for index in range(len(q_list)):
        if q_list[index] == max_q:
            print(max_q, environment[index])

    for index in range(len(q_list)):
        if q_list[index] == max_q:
            next_states.append(index)
    next_state = environment[next_states[random.randint(0, len(next_states) - 1)]]
    # print(q_matrix[state_index][next_state], environment[state_index], environment[next_state])
    for index_1 in range(3):
        for index_2 in range(3):
            index = index_1 * 3 + index_2
            if index in next_state["black"]:
                character_list[index_1][index_2]["type"] = 0
            elif index in next_state["white"]:
                character_list[index_1][index_2]["type"] = 1
            else:
                character_list[index_1][index_2]["type"] = None
    state["player"] = 0
    return state


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
                if room == "ai":
                    next_state = ai_process(data["data"])
                    data["data"] = next_state
                    await manager.send_other_message(data, room)
                else:
                    await manager.send_other_message(data, room)
    except WebSocketDisconnect:
        manager.disconnect(room, ws)

if __name__ == "__main__":
    import uvicorn
    # 官方推荐是用命令后启动 uvicorn main:app --host=127.0.0.1 --port=8010 --reload
    uvicorn.run(app='main:app', host="0.0.0.0", port=8010, reload=True, debug=True)





