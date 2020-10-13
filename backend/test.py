"""
-o---T
# T 就是宝藏的位置, o 是探索者的位置
"""

# 作者: hhh5460
# 时间：20181217
import pandas as pd
import random
import time
import pymysql
import asyncio
import traceback
import aiomysql

epsilon = 0.9  # 贪婪度 greedy
alpha = 0.1  # 学习率
gamma = 0.8  # 奖励递减值

states = range(6)  # 状态集。从0到5
actions = ['left', 'right']  # 动作集。也可添加动作'none'，表示停留
rewards = [0, 0, 0, 0, 0, 1]  # 奖励集。只有最后的宝藏所在位置才有奖励1，其他皆为0

q_table = pd.DataFrame(data=[[0 for _ in actions] for _ in states],
                       index=states, columns=actions)


def update_env(state):
    """更新环境，并打印"""
    global states

    env = list('-----T')  # 环境，就是这样一个字符串(list)！！
    if state != states[-1]:
        env[state] = 'o'
    print('\r{}'.format(''.join(env)), end='')
    time.sleep(0.1)


def get_next_state(state, action):
    """对状态执行动作后，得到下一状态"""
    global states

    # l,r,n = -1,+1,0
    if action == 'right' and state != states[-1]:  # 除非最后一个状态（位置），向右就+1
        next_state = state + 1
    elif action == 'left' and state != states[0]:  # 除非最前一个状态（位置），向左就-1
        next_state = state - 1
    else:
        next_state = state
    return next_state


def get_valid_actions(state):
    """取当前状态下的合法动作集合，与reward无关！"""
    global actions  # ['left', 'right']

    valid_actions = set(actions)
    if state == states[-1]:  # 最后一个状态（位置），则
        valid_actions -= set(['right'])  # 不能向右
    if state == states[0]:  # 最前一个状态（位置），则
        valid_actions -= set(['left'])  # 不能向左
    return list(valid_actions)


def start():
    for i in range(13):
        # current_state = random.choice(states)
        current_state = 0

        update_env(current_state)  # 环境相关
        total_steps = 0  # 环境相关

        while current_state != states[-1]:
            if (random.uniform(0, 1) > epsilon) or ((q_table.iloc[current_state] == 0).all()):  # 探索
                current_action = random.choice(get_valid_actions(current_state))
            else:
                current_action = q_table.iloc[current_state].idxmax()  # 利用（贪婪）

            next_state = get_next_state(current_state, current_action)
            next_state_q_values = q_table.loc[next_state, get_valid_actions(next_state)]
            q_table.loc[current_state, current_action] += alpha * (
                        rewards[next_state] + gamma * next_state_q_values.max() - q_table.loc[current_state, current_action])
            current_state = next_state

            update_env(current_state)  # 环境相关
            total_steps += 1  # 环境相关

        print('\rEpisode {}: total_steps = {}'.format(i, total_steps), end='')  # 环境相关
        time.sleep(2)  # 环境相关
        print('\r                                ', end='')  # 环境相关

    print('\nq_table:')
    print(q_table)


class BaseMysqlFetcher:
    def __init__(self, host, db, user, pwd, port):
        self.host = host
        self.db = db
        self.port = port
        self.user = user
        self.pwd = pwd
        self.client = None
        self.cursor = None
        self.loop = None


class MysqlFetcher(BaseMysqlFetcher):

    def connect(self):
        if not self.client:
            self.client = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.pwd,
                db=self.db,
                port=self.port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
            )

        if not self.cursor:
            self.cursor = self.client.cursor()

    def get_cursor(self):
        if not self.cursor:
            self.cursor = self.client.cursor()

    def close(self):
        self.cursor.close()

    def execute(self, sql):
        self.client.ping(reconnect=True)
        results = self.cursor.execute(sql)
        self.client.commit()
        return results


class AioMysqlFetcher(BaseMysqlFetcher):

    async def get_cursor(self):
        loop = asyncio.get_event_loop()
        client = await aiomysql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            db=self.db,
            port=self.port,
            charset='utf8mb4',
            loop=loop,
            cursorclass=aiomysql.cursors.DictCursor
        )
        return await client.cursor()

    async def execute_fetchall(self, sql):
        cursor = await self.get_cursor()
        try:
            await cursor.execute(sql)
            data = await cursor.fetchall()
            return data
        except Exception as e:
            traceback.print_exc()
            print(e)
        finally:
            await cursor.close()

    def fetchall(self, sqls):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            tasks = [self.execute_fetchall(sql) for sql in sqls]
            results = loop.run_until_complete(asyncio.gather(*tasks))
            return results
        except Exception as e:
            traceback.print_exc()
            print(e)
        finally:
            loop.close()

    async def execute_fetchone(self, sql):
        cursor = await self.get_cursor()
        try:
            await cursor.execute(sql)
            data = await cursor.fetchone()
            return data
        except Exception as e:
            traceback.print_exc()
        finally:
            await cursor.close()

    def fetchone(self, sqls):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            tasks = [self.execute_fetchone(sql) for sql in sqls]
            results = loop.run_until_complete(asyncio.gather(*tasks))
            return results
        except Exception as e:
            traceback.print_exc()
        finally:
            loop.close()