from typing import List, Dict
import numpy as np
import operator
import random


def init_environment():
    characters: List[Dict[str, List[int]]] = []
    normal_list: List[int] = []
    for cell_1 in range(0, 9, 1):
        normal_list.append(cell_1)
        for cell_2 in range(cell_1 + 1, 9, 1):
            for cell_3 in range(cell_2 + 1, 9, 1):
                characters.append({"black": [cell_1, cell_2, cell_3], "white": []})
    for character in characters:
        unavailable_list = character["black"].copy()
        for cell_1 in range(0, 9, 1):
            if cell_1 in unavailable_list:
                continue
            for cell_2 in range(cell_1 + 1, 9, 1):
                if cell_2 in unavailable_list:
                    continue
                for cell_3 in range(cell_2 + 1, 9, 1):
                    if cell_3 in unavailable_list:
                        continue
                    character["white"] = [cell_1, cell_2, cell_3]
    return characters


def init_return_matrix(environment: List[Dict[str, List[int]]]):
    return_matrix = np.zeros((len(environment), len(environment)), int)
    common_win = [[3, 4, 5], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    black_wins = common_win.copy()
    white_wins = common_win.copy()
    black_wins.append([6, 7, 8])
    white_wins.append([0, 1, 2])
    for index_0 in range(len(environment)):
        for black_win in black_wins:
            if operator.eq(environment[index_0], black_win):
                return_matrix[[index_0], :] = -1
                continue
        for white_win in white_wins:
            if operator.eq(environment[index_0], white_win):
                return_matrix[[index_0], :] = 1
                continue
        for index_1 in range(len(environment)):
            cur_state = environment[index_0]
            cur_action = environment[index_1]
            common_counter = 0
            if not operator.eq(cur_state["black"], cur_action["black"]):
                return_matrix[index_0][index_1] = -1
            if operator.eq(cur_state["white"], cur_action["white"]):
                return_matrix[index_0][index_1] = -1
            for index in range(3):
                if cur_state["white"][index] in cur_action["white"]:
                    common_counter += 1
            if common_counter != 1:
                return_matrix[index_0][index_1] = -1
    return return_matrix


def start_train():
    environment = init_environment()
    return_matrix = init_return_matrix(environment)
    q_matrix = np.zeros([len(environment), len(environment)], np.float)
    greed = 0.8
    horizon = 1000

    while horizon < 0:
        state = np.random.randint(0, len(environment))
        next_state_list = []
        for i in range(len(environment)):
            if return_matrix[state][i] != -1:
                next_state_list.append(i)
        if len(next_state_list) > 0:
            next_state = next_state_list[random.randint(0, len(next_state_list) - 1)]
            q[state, next_state] = r[state, next_state] + greed * max(q[next_state])
        horizon -= 1
        if horizon % 100 == 0:
            print(horizon)

    i = 0
    while i < 5:
        state = i
        i = i + 1
        print("robot 处于{}位置".format(state))
        count = 0
        list = []
        while state != 5:
            if count > 11:
                print("failed ! \n")
                break
            list.append(state)
            next_state = q[state].argmax()
            count = count + 1
            state = next_state
        list.append(5)
        print('path is :')
        print
        list

