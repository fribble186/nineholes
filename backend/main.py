from typing import List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import json

import asyncio

import random

import copy

import operator

import AiUtils

import numpy as np

app = FastAPI()

agents = []


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
        if person_in_room == 0 and "ai" in room and room != "train":
            agents.append({
                "room": room,
                "agent": AlphaSJ("agent")
            })
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


class AlphaSJ(object):

    def __init__(self, mode):
        self.agent_black = None
        self.agent_white = None
        self.alpha: float = 0.2
        self.discount: float = 0.9
        self.greedy: float = 0.5
        if mode == "train":
            self.environment: List[Dict[str, List[int]]] = AiUtils.init_environment()
            self.white_r_matrix = AiUtils.init_white_return_matrix(self.environment)
            self.white_q_matrix = AiUtils.init_white_q_matrix(self.environment)
            self.black_p_matrix = AiUtils.init_black_p_matrix(self.environment)
            self.black_r_matrix = AiUtils.init_black_return_matrix(self.environment)

            self.init_state = None
            self.game_count: int = 0
            self.step_count: int = 0
            self.white_route: List[List[int]] = []
            self.black_route: List[List[int]] = []
            self.last_white_action_index: int = -1
        else:
            self.environment: List[Dict[str, List[int]]] = AiUtils.init_environment()
            self.white_r_matrix = np.load("r_matrix.npy")
            self.white_q_matrix = np.load("q_matrix.npy")
            self.black_p_matrix = np.load("p_matrix.npy")
            self.black_r_matrix = AiUtils.init_black_return_matrix(self.environment)

            self.game_count: int = (np.load("count.npy"))[0]
            self.step_count: int = 0
            self.white_route: List[List[int]] = []
            self.black_route: List[List[int]] = []
            self.last_white_action_index: int = -1

    def train(self, new_return):
        print("train\n{}\n{}".format(self.white_route, self.black_route))
        self.game_count += 1
        for route_item in self.white_route:
            if self.white_r_matrix[route_item[0]][route_item[1]] != 1:
                self.white_r_matrix[route_item[0]][route_item[1]] = ((self.game_count - 1) * self.white_r_matrix[route_item[0]][route_item[1]] + new_return) / self.game_count
        # 马尔科夫链根据bellman公式更新表格
        for route_item in self.white_route:
            print("old q: {}".format(self.white_q_matrix[route_item[0]][route_item[1]]))
            self.white_q_matrix[route_item[0]][route_item[1]] = (1 - self.alpha) * self.white_q_matrix[route_item[0]][route_item[1]] + self.alpha * (self.white_r_matrix[route_item[0]][route_item[1]] + self.discount * self.white_q_matrix[route_item[0]].max())
            print("new q: {}".format(self.white_q_matrix[route_item[0]][route_item[1]]))
        # 更新黑子状态转移矩阵
        for route_item in self.black_route:
            print("old p: {}".format(self.black_p_matrix[route_item[0]][route_item[1]]))
            self.black_p_matrix[route_item[0]][route_item[1]] += 1
            print("new p: {}".format(self.black_p_matrix[route_item[0]][route_item[1]]))
        self.last_white_action_index = -1
        self.step_count = 0
        self.black_route = []
        self.white_route = []

    def training_white_agent(self, state):
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
        for index, state_item in enumerate(self.environment):
            if operator.eq(state_item, character):
                state_index = index
                break

        white_r_list = self.white_r_matrix[state_index]
        available_list = []
        win_index = -1

        for index, item in enumerate(white_r_list):
            if white_r_list[index] != -1:
                white_q_list = self.white_q_matrix[index]
                if (white_q_list == 1).all():
                    win_index = index
                available_list.append({
                    "target_action_index": index,
                    "black_state_index": index,
                    "black_r_list": self.black_r_matrix[index],
                    "black_available_list": None,
                    "q": None
                })
        if win_index == -1:
            for available in available_list:
                available["black_available_list"] = [index for index, item in enumerate(available["black_r_list"]) if available["black_r_list"][index] != -1]
            for available in available_list:
                available["q"] = 0
                count = 0
                for black_available in available["black_available_list"]:
                    count += self.black_p_matrix[available["black_state_index"]][black_available]
                for black_available in available["black_available_list"]:
                    white_r_next_list = self.white_r_matrix[black_available]
                    white_q_next_list = self.white_q_matrix[black_available]
                    next_white_available = [index for index, item in enumerate(white_r_next_list) if white_r_next_list[index] != -1]
                    q_available_list = [white_q_next_list[index] for index in next_white_available]
                    if len(q_available_list) == 0:
                        available["q"] += -self.black_p_matrix[available["black_state_index"]][black_available] / count
                    else:
                        available["q"] += (self.black_p_matrix[available["black_state_index"]][black_available] / count) * max(q_available_list)
            if len(available_list) > 0:
                max_q = max([item["q"] for item in available_list])
                next_states = []
                # for index in range(len(q_list)):
                #     if q_list[index] == max_q:
                #         print(max_q, self.environment[index])
                if random.uniform(0, 1) > self.greedy:
                    print("探索")
                    next_states = available_list
                else:
                    print("利用")
                    for available in available_list:
                        if available["q"] == max_q:
                            next_states.append(available)
                next_state_index = random.randint(0, len(next_states) - 1)
                next_state = self.environment[next_states[next_state_index]["target_action_index"]]

                self.white_route.append([state_index, next_states[next_state_index]["target_action_index"]])
                if self.last_white_action_index == -1:
                    # 获取初始state
                    character = {"white": [6, 7, 8], "black": [0, 1, 2]}
                    black_state_index = 0
                    for index, state_item in enumerate(self.environment):
                        if operator.eq(state_item, character):
                            black_state_index = index
                            break
                    self.black_route.append([black_state_index, state_index])
                else:
                    self.black_route.append([self.last_white_action_index, state_index])
                self.last_white_action_index = next_states[next_state_index]["target_action_index"]
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
        else:
            next_state = self.environment[win_index]

            self.white_route.append([state_index, win_index])
            if self.last_white_action_index == -1:
                # 获取初始state
                character = {"white": [6, 7, 8], "black": [0, 1, 2]}
                black_state_index = 0
                for index, state_item in enumerate(self.environment):
                    if operator.eq(state_item, character):
                        black_state_index = index
                        break
                self.black_route.append([black_state_index, state_index])
            else:
                self.black_route.append([self.last_white_action_index, state_index])
            self.last_white_action_index = win_index
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
            state["winner"] = 1
        return state

    def agent_process(self, state):
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
        state_index = 0
        for index, state_item in enumerate(self.environment):
            if operator.eq(state_item, character):
                state_index = index
                break

        white_r_list = self.white_r_matrix[state_index]
        available_list = []
        win_index = -1

        for index, item in enumerate(white_r_list):
            if white_r_list[index] != -1:
                white_q_list = self.white_q_matrix[index]
                if (white_q_list == 1).all():
                    win_index = index
                available_list.append({
                    "target_action_index": index,
                    "black_state_index": index,
                    "black_r_list": self.black_r_matrix[index],
                    "black_available_list": None,
                    "q": None
                })
        if win_index == -1:
            print("no win index")
            for available in available_list:
                available["black_available_list"] = [index for index, item in enumerate(available["black_r_list"]) if
                                                     available["black_r_list"][index] != -1]
            for available in available_list:
                available["q"] = 0
                count = 0
                for black_available in available["black_available_list"]:
                    count += self.black_p_matrix[available["black_state_index"], black_available]
                for black_available in available["black_available_list"]:
                    white_r_next_list = self.white_r_matrix[black_available]
                    white_q_next_list = self.white_q_matrix[black_available]
                    next_white_available = [index for index, item in enumerate(white_r_next_list) if
                                            white_r_next_list[index] != -1]
                    q_available_list = [white_q_next_list[index] for index in next_white_available]
                    if len(q_available_list) == 0:
                        available["q"] += -self.black_p_matrix[available["black_state_index"], black_available] / count
                    else:
                        available["q"] += (self.black_p_matrix[
                                               available["black_state_index"], black_available] / count) * max(
                            q_available_list)
            for available in available_list:
                print(available)
            if len(available_list) > 0:
                max_q = max([item["q"] for item in available_list])
                next_states = []
                # for index in range(len(q_list)):
                #     if q_list[index] == max_q:
                #         print(max_q, self.environment[index])
                for available in available_list:
                    if available["q"] == max_q:
                        next_states.append(available)
                next_state_index = random.randint(0, len(next_states) - 1)
                next_state = self.environment[next_states[next_state_index]["target_action_index"]]

                self.white_route.append([state_index, next_states[next_state_index]["target_action_index"]])
                if self.last_white_action_index == -1:
                    # 获取初始state
                    character = {"white": [6, 7, 8], "black": [0, 1, 2]}
                    black_state_index = 0
                    for index, state_item in enumerate(self.environment):
                        if operator.eq(state_item, character):
                            black_state_index = index
                            break
                    self.black_route.append([black_state_index, state_index])
                else:
                    self.black_route.append([self.last_white_action_index, state_index])
                self.last_white_action_index = next_states[next_state_index]["target_action_index"]
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
        else:
            next_state = self.environment[win_index]

            self.white_route.append([state_index, win_index])
            if self.last_white_action_index == -1:
                # 获取初始state
                character = {"white": [6, 7, 8], "black": [0, 1, 2]}
                black_state_index = 0
                for index, state_item in enumerate(self.environment):
                    if operator.eq(state_item, character):
                        black_state_index = index
                        break
                self.black_route.append([black_state_index, state_index])
            else:
                self.black_route.append([self.last_white_action_index, state_index])
            self.last_white_action_index = win_index
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
            state["winner"] = 1
        return state


manager = WSConnectionManager()
learner = AlphaSJ("train")


@app.websocket("/ws/{room}")
async def websocket_endpoint(ws: WebSocket, room: str):
    await manager.connect(room, ws)

    try:
        while True:
            data = await ws.receive_text()
            data = json.loads(data)
            room = data["room"]
            if room:
                # 与ai对战
                if "ai" in room and room != "train":
                    state = copy.deepcopy(data["data"])
                    for agent_item in agents:
                        if agent_item["room"] == room:
                            agent = agent_item["agent"]
                            if state["winner"] is not None:
                                new_return = 1 / agent.step_count if state["winner"] == 1 else -1 / agent.step_count
                                agent.train(new_return)
                                print("return", new_return)
                                print("game count", agent.game_count)
                                await asyncio.sleep(0.1)
                                await manager.send_other_message("continue", room)
                                AiUtils.save_obj(agent.white_q_matrix, agent.white_r_matrix, agent.black_p_matrix, agent.game_count)
                                print("saved Q")
                            else:
                                if state["player"] == 1:
                                    agent.step_count += 1
                                    state = agent.agent_process(state)
                                if state["winner"] is not None:
                                    new_return = 1 / agent.step_count if state["winner"] == 1 else -1 / agent.step_count
                                    agent.train(new_return)
                                    print("return", new_return)
                                    print("game count", agent.game_count)
                                    await asyncio.sleep(0.1)
                                    AiUtils.save_obj(agent.white_q_matrix, agent.white_r_matrix, agent.black_p_matrix, agent.game_count)
                                    print("saved Q")
                                data["data"] = state
                                await asyncio.sleep(0.1)
                                await manager.send_other_message(data, room)
                # 可视化对抗训练1次
                elif room == "train":
                    state = data["data"]

                    if state["winner"] is not None:
                        new_return = 1 / learner.step_count if state["winner"] == 1 else -1 / learner.step_count
                        learner.train(new_return)
                        print("return", new_return)
                        print("game count", learner.game_count)
                        await asyncio.sleep(0.1)
                        if learner.game_count > 0:
                            AiUtils.save_obj(learner.white_q_matrix, learner.white_r_matrix, learner.black_p_matrix, learner.game_count)
                            print("saved Q")
                        else:
                            await manager.send_other_message("continue", room)
                    else:
                        if state["player"] == 1:
                            learner.step_count += 1
                            state = learner.training_white_agent(state)
                        if state["winner"] is not None:
                            new_return = 1 / learner.step_count if state["winner"] == 1 else -1 / learner.step_count
                            learner.train(new_return)
                            print("return", new_return)
                            print("game count", learner.game_count)
                            await asyncio.sleep(1)
                            if learner.game_count > 0:
                                AiUtils.save_obj(learner.white_q_matrix, learner.white_r_matrix, learner.black_p_matrix, learner.game_count)
                                print("saved Q")
                        if learner.game_count <= 0:
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
