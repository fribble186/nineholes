# 田字棋

## 简介

* 使用react+typescript做为前端展示（训练时也可以展示）
* 使用fastapi做websocket服务器
* 使用强化学习，黑白子对抗来学习生成q表格和状态转移概率矩阵（最简单的表格法）

## 改进思路

```
学习过程伪代码（白子为训练目标）
黑白子博弈，白子下棋次数n，r矩阵（行：state_index，列：action_index），q矩阵与r同型
增加了状态转移层，每一次对局按照马尔科夫链进行更新
贪婪程度：greedy
学习率: alpha
损耗率: discount
for 每一步 in 博弈过程：
	if random(0,1) < greddy:
		利用=>得到action
	else:
		探索=>得到action
	更新白子路径
	更新黑子路径
博弈结束时：
	总局数game_count++
	如果白子赢了，新的Rrturn = 1 / n
	如果黑子赢了，新的Return = -1 / n
	更新r矩阵
	for state_index, action_index in 白子下棋路径：
		r[state_index][action_index] = ((game_count - 1) * r[state_index][action_index] + 新的Ruturn ) / game_count
	更新p矩阵
	for state_index, action_index in 黑子下棋路径：
		p[state_index][action_index] ++
	更新q矩阵
	for state_index, action_index in 白子下棋路径：
		q[state_index][action_index] = (1 - alpha) * q[state_index][action_index] + alpha * (r[state_index][action_index] + SUM(p[action_index][next_state_index] * max(q[next_state_index])))
```

## 错误思路

```
学习过程伪代码（白子为训练目标）
黑白子博弈，白子下棋次数n，r矩阵（行：state_index，列：action_index），q矩阵与r同型
如果白子赢了，新的Rrturn = 1 / n
如果黑子赢了，新的Return = -1 / n
更新r矩阵
for state_index, action_index in 白子下棋路径：
	r[state_index][action_index] = 1 / 2 ( r[state_index][action_index] + 新的Ruturn )
更新q矩阵
for index in range(学习次数):
	获得random_state_index
	for action_index in 可以走的action(random_state_index):
		q[random_state_index][action_index] =  (1-学习率) * q[random_state_index][action_index] + 学习率 * (r[random_state_index][action_index] + 时间损失 * q[action_index].MAX)
```

## 注意事项

* 环境安装好后，react工程下需自己写config文件，对应fastapi的websocket服务器地址
* 环境安装好后，可以本地运行domain/train，跑出自己的学习结果
