"""
生成棋盘所有的环境
生成白子和黑子的收益矩阵，r matrix
测试和保存期望收益举证，q matrix
"""
from typing import List, Dict
import numpy as np
import operator
import pickle


def init_environment():
    """
    生成所有的棋盘情况，C93 * C63 1680种情况
    """
    characters: List[Dict[str, List[int]]] = []
    blacks = []
    normal_list: List[int] = []
    # 黑子的所有情况
    for cell_1 in range(0, 9, 1):
        normal_list.append(cell_1)
        for cell_2 in range(cell_1 + 1, 9, 1):
            for cell_3 in range(cell_2 + 1, 9, 1):
                blacks.append([cell_1, cell_2, cell_3])

    # 除了黑子占用的，白子的所有情况
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


def init_white_rule_matrix(environment: List[Dict[str, List[int]]]):
    """
    生成1680 * 1680的白子 规则 矩阵，其中
    0是可以走的格子
    1是白子赢的格子
    -1是白子输的格子
    """
    return_matrix = np.zeros((len(environment), len(environment)), float)
    common_win = [[3, 4, 5], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    black_wins = common_win.copy()
    white_wins = common_win.copy()
    black_wins.append([6, 7, 8])  # 黑子赢的情况
    white_wins.append([0, 1, 2])  # 白子赢的情况

    for index_0 in range(len(environment)):
        for black_win in black_wins:  # 黑子赢的state行为-1
            if operator.eq(environment[index_0]["black"], black_win):
                return_matrix[[index_0], :] = -1
        if return_matrix[[index_0], 0] == -1:
            continue
        for white_win in white_wins:  # 白子赢的state行为1
            if operator.eq(environment[index_0]["white"], white_win):
                return_matrix[[index_0], :] = 1
        if return_matrix[[index_0], 0] == 1:
            continue

        for index_1 in range(len(environment)):
            can_move = False
            cur_state = environment[index_0]  # 当前state
            cur_action = environment[index_1]  # 当前action
            common_counter = 0  # 记录多少个白子是相同的
            diff_index = []

            # 规则
            if operator.eq(cur_state["black"], cur_action["black"]):  # 黑子不能动
                if not operator.eq(cur_state["white"], cur_action["white"]):  # 白子必须动
                    for index in range(3):  # 白子只能动一步
                        if cur_state["white"][index] in cur_action["white"]:
                            common_counter += 1
                    for cur_state_index in range(3):
                        for cur_action_index in range(3):
                            if (cur_state["white"][cur_state_index] not in cur_action["white"]) and (
                                    cur_action["white"][cur_action_index] not in cur_state["white"]):
                                diff_index = [cur_state["white"][cur_state_index],
                                              cur_action["white"][cur_action_index]]
                    if common_counter == 2:
                        if abs(diff_index[0] - diff_index[1]) == 1:
                            diff_index.sort()
                            if not operator.eq(diff_index, [2, 3]) and not operator.eq(diff_index, [5, 6]):
                                can_move = True
                        if abs(diff_index[0] - diff_index[1]) == 3:
                            can_move = True
                        if diff_index[0] in [0, 4, 8] and diff_index[1] in [0, 4, 8] and abs(
                                diff_index[0] - diff_index[1]) == 4:
                            can_move = True
                        if diff_index[0] in [2, 4, 6] and diff_index[1] in [2, 4, 6] and abs(
                                diff_index[0] - diff_index[1]) == 2:
                            can_move = True

            if can_move:
                return_matrix[index_0][index_1] = 0
                for white_win in white_wins:  # 白子赢的情况
                    if operator.eq(cur_action["white"], white_win):
                        return_matrix[index_0][index_1] = 1
            else:
                return_matrix[index_0][index_1] = -1

    return return_matrix


def init_white_return_matrix(environment: List[Dict[str, List[int]]]):
    """
    生成1680 * 1680的白子 return 矩阵，其中
    0是可以走的格子
    1是白子赢的格子
    -1是白子输的格子
    """
    return_matrix = np.zeros((len(environment), len(environment)), float)
    common_win = [[3, 4, 5], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    black_wins = common_win.copy()
    white_wins = common_win.copy()
    black_wins.append([6, 7, 8])  # 黑子赢的情况
    white_wins.append([0, 1, 2])  # 白子赢的情况

    for index_0 in range(len(environment)):
        for black_win in black_wins:  # 黑子赢的state行为-1
            if operator.eq(environment[index_0]["black"], black_win):
                return_matrix[[index_0], :] = -1
        if return_matrix[[index_0], 0] == -1:
            continue
        for white_win in white_wins:  # 白子赢的state行为1
            if operator.eq(environment[index_0]["white"], white_win):
                return_matrix[[index_0], :] = 1
        if return_matrix[[index_0], 0] == 1:
            continue

        for index_1 in range(len(environment)):
            can_move = False
            cur_state = environment[index_0]  # 当前state
            cur_action = environment[index_1]  # 当前action
            common_counter = 0  # 记录多少个白子是相同的
            diff_index = []

            # 规则
            if operator.eq(cur_state["black"], cur_action["black"]):  # 黑子不能动
                if not operator.eq(cur_state["white"], cur_action["white"]):  # 白子必须动
                    for index in range(3):  # 白子只能动一步
                        if cur_state["white"][index] in cur_action["white"]:
                            common_counter += 1
                    for cur_state_index in range(3):
                        for cur_action_index in range(3):
                            if (cur_state["white"][cur_state_index] not in cur_action["white"]) and (cur_action["white"][cur_action_index] not in cur_state["white"]):
                                diff_index = [cur_state["white"][cur_state_index], cur_action["white"][cur_action_index]]
                    if common_counter == 2:
                        if abs(diff_index[0] - diff_index[1]) == 1:
                            diff_index.sort()
                            if not operator.eq(diff_index, [2,3]) and not operator.eq(diff_index, [5,6]):
                                can_move = True
                        if abs(diff_index[0] - diff_index[1]) == 3:
                            can_move = True
                        if diff_index[0] in [0,4,8] and diff_index[1] in [0,4,8] and abs(diff_index[0] - diff_index[1]) == 4:
                            can_move = True
                        if diff_index[0] in [2,4,6] and diff_index[1] in [2,4,6] and abs(diff_index[0] - diff_index[1]) == 2:
                            can_move = True

            if can_move:
                return_matrix[index_0][index_1] = 0
                for white_win in white_wins:  # 白子赢的情况
                    if operator.eq(cur_action["white"], white_win):
                        return_matrix[index_0][index_1] = 1
            else:
                return_matrix[index_0][index_1] = -1

    return return_matrix


def init_white_q_matrix(environment: List[Dict[str, List[int]]]):
    """
    生成1680 * 1680的白子 return 矩阵，其中
    0是可以走的格子
    1是白子赢的格子
    -1是白子输的格子
    """
    return_matrix = np.zeros((len(environment), len(environment)), float)
    common_win = [[3, 4, 5], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    black_wins = common_win.copy()
    white_wins = common_win.copy()
    black_wins.append([6, 7, 8])  # 黑子赢的情况
    white_wins.append([0, 1, 2])  # 白子赢的情况

    for index_0 in range(len(environment)):
        for black_win in black_wins:  # 黑子赢的state行为-1
            if operator.eq(environment[index_0]["black"], black_win):
                return_matrix[[index_0], :] = -1
        if return_matrix[[index_0], 0] == -1:
            continue
        for white_win in white_wins:  # 白子赢的state行为1
            if operator.eq(environment[index_0]["white"], white_win):
                return_matrix[[index_0], :] = 1
        if return_matrix[[index_0], 0] == 1:
            continue

        for index_1 in range(len(environment)):
            can_move = False
            cur_state = environment[index_0]  # 当前state
            cur_action = environment[index_1]  # 当前action
            common_counter = 0  # 记录多少个白子是相同的
            diff_index = []

            # 规则
            if operator.eq(cur_state["black"], cur_action["black"]):  # 黑子不能动
                if not operator.eq(cur_state["white"], cur_action["white"]):  # 白子必须动
                    for index in range(3):  # 白子只能动一步
                        if cur_state["white"][index] in cur_action["white"]:
                            common_counter += 1
                    for cur_state_index in range(3):
                        for cur_action_index in range(3):
                            if (cur_state["white"][cur_state_index] not in cur_action["white"]) and (cur_action["white"][cur_action_index] not in cur_state["white"]):
                                diff_index = [cur_state["white"][cur_state_index], cur_action["white"][cur_action_index]]
                    if common_counter == 2:
                        if abs(diff_index[0] - diff_index[1]) == 1:
                            diff_index.sort()
                            if not operator.eq(diff_index, [2,3]) and not operator.eq(diff_index, [5,6]):
                                can_move = True
                        if abs(diff_index[0] - diff_index[1]) == 3:
                            can_move = True
                        if diff_index[0] in [0,4,8] and diff_index[1] in [0,4,8] and abs(diff_index[0] - diff_index[1]) == 4:
                            can_move = True
                        if diff_index[0] in [2,4,6] and diff_index[1] in [2,4,6] and abs(diff_index[0] - diff_index[1]) == 2:
                            can_move = True

            if can_move:
                return_matrix[index_0][index_1] = 0
                for white_win in white_wins:  # 白子赢的情况
                    if operator.eq(cur_action["white"], white_win):
                        return_matrix[index_0][index_1] = 1
            else:
                return_matrix[index_0][index_1] = -1

    return return_matrix


def init_black_return_matrix(environment: List[Dict[str, List[int]]]):
    """
    生成1680 * 1680的黑子 return 矩阵，其中
    """
    return_matrix = np.zeros((len(environment), len(environment)), float)
    common_win = [[3, 4, 5], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    black_wins = common_win.copy()
    white_wins = common_win.copy()
    black_wins.append([6, 7, 8])
    white_wins.append([0, 1, 2])

    for index_0 in range(len(environment)):
        for black_win in black_wins:  # 黑子赢的state+1
            if operator.eq(environment[index_0]["black"], black_win):
                return_matrix[[index_0], :] = 1
        if return_matrix[[index_0], 0] == 1:
            continue
        for white_win in white_wins:  # 白子赢的state-1
            if operator.eq(environment[index_0]["white"], white_win):
                return_matrix[[index_0], :] = -1
        if return_matrix[[index_0], 0] == -1:
            continue

        for index_1 in range(len(environment)):
            can_move = False
            cur_state = environment[index_0]  # 当前state
            cur_action = environment[index_1]  # 当前action
            common_counter = 0  # 记录多少个黑子是相同的
            diff_index = []

            # 规则
            if operator.eq(cur_state["white"], cur_action["white"]):  # 白子不能动
                if not operator.eq(cur_state["black"], cur_action["black"]):  # 黑子必须动
                    for index in range(3):  # 黑子只能动一步
                        if cur_state["black"][index] in cur_action["black"]:
                            common_counter += 1
                    for cur_state_index in range(3):
                        for cur_action_index in range(3):
                            if (cur_state["black"][cur_state_index] not in cur_action["black"]) and (
                                    cur_action["black"][cur_action_index] not in cur_state["black"]):
                                diff_index = [cur_state["black"][cur_state_index],
                                              cur_action["black"][cur_action_index]]
                    if common_counter == 2:
                        if abs(diff_index[0] - diff_index[1]) == 1:
                            diff_index.sort()
                            if not operator.eq(diff_index, [2, 3]) and not operator.eq(diff_index, [5, 6]):
                                can_move = True
                        if abs(diff_index[0] - diff_index[1]) == 3:
                            can_move = True
                        if diff_index[0] in [0, 4, 8] and diff_index[1] in [0, 4, 8] and abs(
                                diff_index[0] - diff_index[1]) == 4:
                            can_move = True
                        if diff_index[0] in [2, 4, 6] and diff_index[1] in [2, 4, 6] and abs(
                                diff_index[0] - diff_index[1]) == 2:
                            can_move = True

            if can_move:
                return_matrix[index_0][index_1] = 0
                for black_win in black_wins:  # 黑子赢的情况
                    if operator.eq(cur_action["black"], black_win):
                        return_matrix[index_0][index_1] = 1
            else:
                return_matrix[index_0][index_1] = -1

    return return_matrix


def init_black_p_matrix(environment: List[Dict[str, List[int]]]):
    """
    生成1680 * 1680的黑子的初始 状态转移 矩阵，其中
    """
    return np.ones((len(environment), len(environment)), float)


def test(q):
    """
    测试查看q矩阵的概况
    调试时使用
    """
    a = {0: 0, 1: 0, 2: 0, 3: 0, 3.5: 0, 4: 0, 4.5: 0, 5: 0}
    for i in range(1680):
        for j in range(1680):
            if q[i][j] == 0:
                a[0] += 1
            elif q[i][j] == 1:
                a[1] += 1
            elif q[i][j] != -1 and q[i][j] != 0 and q[i][j] != 1:
                if q[i][j] < 0:
                    a[2] += 1
                else:
                    a[3] += 1
    print(a)


def save_obj(q, r, p, count):
    """
    保存q矩阵和所有棋盘情况
    """
    np.save("q_matrix.npy", q)
    np.save("r_matrix.npy", r)
    np.save("p_matrix.npy", p)
    np.save("count.npy", np.array([count]))


# r = init_return_matrix(init_environment())
# np.set_printoptions(threshold=np.inf)
# print(r)
# q = start_train()
# test(q)

