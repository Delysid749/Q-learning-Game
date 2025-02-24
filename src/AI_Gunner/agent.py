import os
import json
import random


class QLearningAgent:
    def __init__(self, state_size, action_size):
        """
        初始化 Q-learning 代理
        :param state_size: 状态空间的大小
        :param action_size: 动作空间的大小
        """
        self.state_size = state_size  # 状态空间的大小
        self.action_size = action_size  # 动作空间的大小
        self.alpha = 0.7  # 初始学习率，用于控制更新 Q 值时的步长
        self.gamma = 0.95  # 折扣因子，用于评估未来奖励的价值
        self.epsilon = 0.995  # 初始探索率，决定代理选择探索还是利用
        self.epsilon_decay = 0.999  # epsilon 的衰减系数，每次更新后减少 epsilon 的值
        self.epsilon_min = 0.01  # epsilon 的最小值，防止探索率过低

        self.action_dist = {0: 0, 1: 0, 2: 0}  # 初始化动作分布，记录每个动作选择的频率

        # 动态学习率参数
        self.alpha_decay = 0.9995  # 学习率衰减系数
        self.alpha_min = 0.1  # 学习率的最小值，防止学习率降得太低

        self.q_table = {}  # Q 表，存储每个状态-动作对的 Q 值
        self.q_table_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'q_value.json')  # Q 表存储路径

        self.moves = []  # 用于记录当前回合中的状态-动作对，方便后续更新 Q 值

    def decay_parameters(self):
        """
        更新探索率 (epsilon) 和学习率 (alpha)，使其逐渐衰减
        """
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)  # 更新 epsilon，防止过度探索
        self.alpha = max(self.alpha_min, self.alpha * self.alpha_decay)  # 更新学习率，避免过早停止学习

    def get_q(self, state, action):
        """
        获取指定状态和动作的 Q 值，如果状态-动作对不存在，则返回 0

        :param state: 当前状态
        :param action: 当前动作
        :return: 对应的 Q 值
        """
        state = str(state)  # 将状态转换为字符串形式，作为字典的键
        return self.q_table.get(state, {}).get(action, 0.0)  # 返回该状态下指定动作的 Q 值，若无则返回 0.0

    def update_q(self, state, action, reward, next_state):
        """
        更新 Q 表中的 Q 值，使用 Q-learning 更新公式

        :param state: 当前状态
        :param action: 当前动作
        :param reward: 当前回合的即时奖励
        :param next_state: 下一状态
        """
        state = str(state)  # 将状态转换为字符串形式
        next_state = str(next_state)  # 将下一状态转换为字符串形式
        # 获取下一状态的最大 Q 值，若该状态没有任何动作，则最大 Q 值为 0
        max_next_q = max(self.q_table.get(next_state, {}).values(), default=0)
        old_q = self.get_q(state, action)  # 获取当前状态-动作对的旧 Q 值
        # 根据 Q-learning 的更新公式计算新的 Q 值
        new_q = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)
        # 更新 Q 表
        self.q_table.setdefault(state, {})[action] = new_q

    def choose_action(self, state):
        """
        根据 epsilon-greedy 策略选择一个动作

        :param state: 当前状态
        :return: 选择的动作
        """
        state = str(state)  # 将状态转换为字符串形式
        if random.random() < self.epsilon:  # 以 epsilon 的概率选择探索
            return random.randint(0, self.action_size - 1)  # 随机选择一个动作
        else:  # 否则选择当前 Q 值最大的动作
            actions = self.q_table.get(state, {})
            if actions:  # 如果该状态下有记录的动作
                action = max(actions, key=actions.get)  # 选择 Q 值最大的动作
            else:
                return 0  # 如果该状态没有记录动作，则选择默认动作

        # 更新动作分布
        if action not in self.action_dist:
            self.action_dist[action] = 0  # 如果该动作没有记录，则初始化为 0
        self.action_dist[action] += 1  # 更新该动作的选择频率
        return action

    def save(self):
        """
        将 Q 表保存到指定文件
        """
        os.makedirs(os.path.dirname(self.q_table_path), exist_ok=True)
        with open(self.q_table_path, "w") as f:
            json.dump(self.q_table, f, indent=4)  # 将 Q 表以 JSON 格式写入文件

    def load(self):
        """
        从文件加载 Q 表
        """
        try:
            with open(self.q_table_path, "r") as f:
                self.q_table = json.load(f)
        except FileNotFoundError:
            pass

    def store_move(self, state, action):
        """
        记录当前状态和动作对，保存到 moves 列表中

        :param state: 当前状态
        :param action: 当前选择的动作
        """
        self.moves.append((state, action))  # 将当前状态和动作对存储到 moves 中

    def update_scores(self, reward, next_state):
        """
        更新 Q 值：通过回顾当前回合中的所有状态-动作对并进行 Q 值更新

        :param reward: 当前回合的最终奖励
        :param next_state: 结束时的状态（可作为参考）
        """
        history = list(reversed(self.moves))  # 反向遍历历史记录
        for state, action in history:
            self.update_q(state, action, reward, next_state)  # 对每个状态-动作对更新 Q 值
        self.moves = []  # 清空历史记录，开始下一回合
