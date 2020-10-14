from typing import List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import json

import asyncio

app = FastAPI()


class WSConnectionManager:
    """
    web socket连接的管理类
    """

    def __init__(self):
        self.active_connections: List[Dict[str, WebSocket]] = []

    async def connect(self, room: str, ws: WebSocket):  # 开始连接
        await ws.accept()
        person_in_room = 0
        for connection in self.active_connections:
            if connection["room"] == room:
                person_in_room += 1
        await ws.send_text(str(person_in_room))  # 返回这个房间已经有几个人，人数限制交给前端进行处理
        self.active_connections.append({"room": room, "ws": ws})

    def disconnect(self, room: str, ws: WebSocket):  # 结束连接
        self.active_connections.remove({"room": room, "ws": ws})

    @staticmethod
    async def send_personal_message(message: dict, ws: WebSocket):  # 给某个用户连接发送信息
        await ws.send_json(message)

    async def send_other_message(self, message: dict, room: str):  # 给房间里所有的用户发送信息
        for connection in self.active_connections:
            if connection["room"] == room:
                await connection['ws'].send_json(message)

    async def broadcast(self, data: dict):  # 给服务器中所有用户发送信息
        for connection in self.active_connections:
            await connection["ws"].send_json(data)


def ai_process(state):
    """
    处理ai下棋的逻辑
    判断当前state，通过期望收益矩阵，使用贪婪策略去拿最优的下一步action
    """
    import pickle
    import numpy as np
    import random
    import copy
    import ai

    # 处理得到当前state
    state = copy.deepcopy(state)
    character_list = state["character_list"]
    blacks = []
    whites = []
    for index_1 in range(3):
        for index_2 in range(3):
            index = index_1 * 3 + index_2
            if character_list[index_1][index_2]["type"] == 0:
                blacks.append(index)
            elif character_list[index_1][index_2]["type"] == 1:
                whites.append(index)
    character = {"white": whites, "black": blacks}

    # 从本地拿到期望收益矩阵，q matrix
    f = open('Q.data', 'rb')
    obj = pickle.load(f)
    environment = obj["environment"]
    q_matrix = np.mat(obj["q_matrix"])

    # 得到q matrix中的state index
    state_index = 0
    for environment_item in environment:
        if environment_item["white"] == character["white"] and environment_item["black"] == character["black"]:
            break
        else:
            state_index += 1

    # 通过白子的收益矩阵，去判断可行
    white_r_matrix = ai.init_return_matrix(environment)
    r_list = white_r_matrix[state_index]
    q_list = q_matrix[state_index]
    q_list = q_list.tolist()
    q_list = q_list[0]
    available_list = [index for index, item in enumerate(r_list) if r_list[index] != -1]
    q_available_list = [q_list[index] for index in available_list]

    # 贪婪策略找到对应state中的最大的期望收益的action
    if len(available_list) > 0:
        max_q = max(q_available_list)
        next_states = []
        for index in range(len(q_list)):
            if q_list[index] == max_q:
                print(max_q, environment[index])
        if random.uniform(0, 1) > 0.9:
            next_states = available_list
        else:
            for index in range(len(q_list)):
                if q_list[index] == max_q:
                    next_states.append(index)
        next_state_index = random.randint(0, len(next_states) - 1)
        next_state = environment[next_states[next_state_index]]
    else:
        state["winner"] = 0

    # 转换成前端需要的数据格式
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


def train_ai(environment, black_q_matrix, white_q_matrix, white_r_matrix, state, route):
    """
    训练对抗的函数
    :environment: 所有棋盘情况
    :black_q_matrix: 黑子的期望收益矩阵 = 白子的收益矩阵
    :white_q_matrix: 白子的期望收益矩阵
    :white_r_matrix: 白子的收益矩阵
    :state: 当前state
    :route: 记录白子下棋路径
    """
    import operator
    import random
    import copy

    state = copy.deepcopy(state)
    character_list = state["character_list"]
    blacks = []
    whites = []

    # 获取state
    for index_1 in range(3):
        for index_2 in range(3):
            index = index_1 * 3 + index_2
            if character_list[index_1][index_2]["type"] == 0:
                blacks.append(index)
            elif character_list[index_1][index_2]["type"] == 1:
                whites.append(index)
    character = {"white": whites, "black": blacks}
    state_index = 0
    for index, state_item in enumerate(environment):
        if operator.eq(state_item, character):
            state_index = index
            break

    # 黑子下棋
    if state["player"] == 0:
        q_list = black_q_matrix[state_index]
        max_q = max(q_list)
        if max_q >= 0:
            next_states = []
            for index in range(len(q_list)):
                if q_list[index] == max_q:
                    next_states.append(index)
            next_state = environment[next_states[random.randint(0, len(next_states) - 1)]]
            for index_1 in range(3):
                for index_2 in range(3):
                    index = index_1 * 3 + index_2
                    if index in next_state["black"]:
                        character_list[index_1][index_2]["type"] = 0
                    elif index in next_state["white"]:
                        character_list[index_1][index_2]["type"] = 1
                    else:
                        character_list[index_1][index_2]["type"] = None
            state["player"] = 1
        else:
            state["winner"] = 1
        return state

    # 白子下棋
    elif state["player"] == 1:
        q_list = white_q_matrix[state_index]
        r_list = white_r_matrix[state_index]
        available_list = [index for index, item in enumerate(r_list) if r_list[index] != -1]
        q_available_list = [q_list[index] for index in available_list]
        if len(available_list) > 0:
            max_q = max(q_available_list)
            next_states = []
            for index in range(len(q_list)):
                if q_list[index] == max_q:
                    print(max_q, environment[index])
            if random.uniform(0, 1) > 0.9:
                next_states = available_list
            else:
                for index in range(len(q_list)):
                    if q_list[index] == max_q:
                        next_states.append(index)
            next_state_index = random.randint(0, len(next_states) - 1)
            next_state = environment[next_states[next_state_index]]
            route.append([state_index, next_states[next_state_index]])
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
        else:
            state["winner"] = 0
        return state


manager = WSConnectionManager()


@app.websocket("/ws/{room}")
async def websocket_endpoint(ws: WebSocket, room: str):
    await manager.connect(room, ws)
    import ai
    import copy
    import random
    environment = ai.init_environment()
    black_r_matrix = ai.init_black_matrix(environment)
    white_r_matrix = ai.init_return_matrix(environment)
    black_q_matrix = copy.deepcopy(black_r_matrix)
    white_q_matrix = copy.deepcopy(white_r_matrix)
    try:
        while True:
            data = await ws.receive_text()
            data = json.loads(data)
            room = data["room"]
            if room:
                # 与ai对战
                if "ai" in room:
                    next_state = ai_process(data["data"])
                    data["data"] = next_state
                    await manager.send_other_message(data, room)
                # 可视化对抗训练500次
                elif room == "train":
                    state = data["data"]
                    game_count = 0
                    step_count = 0
                    init_state = copy.deepcopy(state)
                    route: List[List[int]] = []
                    alpha = 0.1
                    discount = 0.9

                    while True:
                        if state["winner"] is not None:
                            r = 1 / step_count if state["winner"] == 1 else -1 / step_count
                            print(route, r)
                            for route_item in route:
                                white_r_matrix[route_item[0]][route_item[1]] = (white_r_matrix[route_item[0]][
                                                                                      route_item[1]] + r) / 2
                            # print("train asc")
                            # for state_index in range(len(environment)):
                            #     next_actions = []
                            #     for action in range(len(environment)):
                            #         if white_r_matrix[state_index][action] > -1:
                            #             next_actions.append(action)
                            #     if len(next_actions) == 0:
                            #         continue
                            #     for next_index in range(len(next_actions)):
                            #         next_state = next_actions[next_index]
                            #         white_q_matrix[state_index][next_state] = (1 - alpha) * white_q_matrix[state_index][next_state] + alpha * (white_r_matrix[state_index][next_state] + discount * (white_q_matrix[next_state]).max())
                            #
                            # print("train desc")
                            # for state_index in range(len(environment) - 1, -1, -1):
                            #     next_actions = []
                            #     for action in range(len(environment)):
                            #         if white_r_matrix[state_index][action] > -1:
                            #             next_actions.append(action)
                            #     if len(next_actions) == 0:
                            #         continue
                            #     for next_index in range(len(next_actions)):
                            #         next_state = next_actions[next_index]
                            #         white_q_matrix[state_index][next_state] = (1 - alpha) * white_q_matrix[state_index][next_state] + alpha * (white_r_matrix[state_index][next_state] + discount * (white_q_matrix[next_state]).max())

                            # bellman公式更新表格
                            print("train random")
                            for random_index in range(1000 * 10):
                                state_index = random.randint(0, len(environment) - 1)
                                next_actions = []
                                for action in range(len(environment)):
                                    if white_r_matrix[state_index][action] > -1:
                                        next_actions.append(action)
                                if len(next_actions) == 0:
                                    continue
                                for next_index in range(len(next_actions)):
                                    next_state = next_actions[next_index]
                                    white_q_matrix[state_index][next_state] = (1 - alpha) * white_q_matrix[state_index][next_state] + alpha * (white_r_matrix[state_index][next_state] + discount * (white_q_matrix[next_state]).max())

                            step_count = 0
                            game_count += 1
                            route = []
                            state = copy.deepcopy(init_state)
                            data["data"] = state
                            # ai.test(white_q_matrix)

                            print("game count", game_count)
                            await asyncio.sleep(0.1)
                            await manager.send_other_message(data, room)
                            if game_count > 500:
                                ai.save_obj(white_q_matrix)
                                print("save Q")
                                break
                        else:
                            if state["player"] == 1:
                                step_count += 1
                            state = train_ai(environment, black_q_matrix, white_q_matrix, white_r_matrix, state, route)
                            data["data"] = state
                            await asyncio.sleep(0.1)
                            await manager.send_other_message(data, room)
                # 正常与别人对战
                else:
                    await manager.send_other_message(data, room)
    except WebSocketDisconnect:
        manager.disconnect(room, ws)


# 启动server
if __name__ == "__main__":
    import uvicorn

    # 官方推荐是用命令后启动 uvicorn main:app --host=127.0.0.1 --port=8010 --reload
    uvicorn.run(app='main:app', host="0.0.0.0", port=8010, reload=True, debug=True)
