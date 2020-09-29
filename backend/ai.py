from typing import List, Dict
import numpy as np
import operator
import random


def init_environment():
    characters: List[Dict[str, List[int]]] = []
    blacks = []
    normal_list: List[int] = []
    for cell_1 in range(0, 9, 1):
        normal_list.append(cell_1)
        for cell_2 in range(cell_1 + 1, 9, 1):
            for cell_3 in range(cell_2 + 1, 9, 1):
                blacks.append([cell_1, cell_2, cell_3])

    for black in blacks:
        unavailable_list = black.copy()
        for cell_1 in range(0, 9, 1):
            if cell_1 in unavailable_list:
                continue
            for cell_2 in range(cell_1 + 1, 9, 1):
                if cell_2 in unavailable_list:
                    continue
                for cell_3 in range(cell_2 + 1, 9, 1):
                    if cell_3 in unavailable_list:
                        continue
                    characters.append({"black": black, "white": [cell_1, cell_2, cell_3]})
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
            if operator.eq(environment[index_0]["black"], black_win):
                return_matrix[[index_0], :] = -1
        if return_matrix[[index_0], 0] == -1:
            continue
        for white_win in white_wins:
            if operator.eq(environment[index_0]["white"], white_win):
                return_matrix[[index_0], :] = 1
        if return_matrix[[index_0], 0] == 1:
            continue

        for index_1 in range(len(environment)):
            cur_state = environment[index_0]
            cur_action = environment[index_1]
            common_counter = 0
            if not operator.eq(cur_state["black"], cur_action["black"]):
                return_matrix[index_0][index_1] = -1
                continue
            if operator.eq(cur_state["white"], cur_action["white"]):
                return_matrix[index_0][index_1] = -1
                continue
            for white_win in white_wins:
                if operator.eq(cur_action["white"], white_win):
                    return_matrix[index_0][index_1] = 1
            diff_index = 0
            for index in range(3):
                if cur_state["white"][index] in cur_action["white"]:
                    common_counter += 1
                else:
                    diff_index = index
            if common_counter != 2:
                return_matrix[index_0][index_1] = -1
                continue
            if abs(cur_state["white"][diff_index]-cur_action["white"][diff_index]) != 1:
                if abs(cur_state["white"][diff_index] - cur_action["white"][diff_index]) != 3:
                    if not ((cur_state["white"][diff_index] in [0, 4, 8] and cur_action["white"][diff_index] in [0, 4, 8]) or (cur_state["white"][diff_index] in [2, 4, 6] and cur_action["white"][diff_index] in [2, 4, 6])):
                        return_matrix[index_0][index_1] = -1
                    return_matrix[index_0][index_1] = -1
                return_matrix[index_0][index_1] = -1

    return return_matrix


def start_train():
    environment = init_environment()
    return_matrix = init_return_matrix(environment)
    q_matrix = np.zeros([len(environment), len(environment)], np.float)
    discount = 0.8
    horizon = len(environment) * len(environment)

    for i in range(horizon):
        state = random.randint(0, len(environment)-1)
        next_actions = []
        for action in range(len(environment)):
            if return_matrix[state][action] >= 0:
                next_actions.append(action)
        print(i)
        if len(next_actions) == 0:
            continue
        for next_index in range(len(next_actions)):
            next_state = next_actions[next_index]
            q_matrix[state][next_state] = return_matrix[state][next_state] + discount * (q_matrix[next_state]).max()

    return q_matrix


q = start_train()
test = {0: 0, 1: 0, 2: 0, 3: 0, 3.5: 0, 4: 0, 4.5: 0, 5: 0}
for i in range(1680):
    for j in range(1680):
        if q[i][j] == 0:
            test[0] += 1
        elif q[i][j] == 1:
            test[1] += 1
        elif 2 < q[i][j] < 3:
            test[2] += 1
        elif 3 < q[i][j] < 3.5:
            test[3] += 1
        elif 3.5 < q[i][j] < 4:
            test[3.5] += 1
        elif 4 < q[i][j] < 4.5:
            test[4] += 1
        elif 4.5 < q[i][j] < 5:
            test[4.5] += 1
        elif q[i][j] > 5:
            test[5] += 1
print(test)
