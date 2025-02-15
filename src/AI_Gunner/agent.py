import os

import numpy as np
import json
import random
from logs_config.log_config import q_value_logger

class QLearningAgent:
    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.95, epsilon=1.0, epsilon_decay=0.995):
        self.state_size = state_size
        self.action_size = action_size
        self.alpha = alpha  # 学习率
        self.gamma = gamma  # 折扣因子
        self.epsilon = epsilon  # 探索率
        self.epsilon_decay = epsilon_decay
        self.q_table = {}
        self.q_table_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'q_value.json')

    def get_q(self, state, action):
        state = str(state)  #  确保 state 作为字符串存储
        return self.q_table.get(state, {}).get(action, 0.0)

    def update_q(self, state, action, reward, next_state):
        state = str(state)  #  确保 state 作为字符串存储
        next_state = str(next_state)
        max_next_q = max(self.q_table.get(next_state, {}).values(), default=0)
        old_q = self.get_q(state, action)
        new_q = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)
        self.q_table.setdefault(state, {})[action] = new_q

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)  # 随机探索
        else:
            return max(self.q_table.get(state, {}), key=self.q_table.get(state, {}).get, default=0)  # 选择最优动作

    def decay_epsilon(self):
        self.epsilon *= self.epsilon_decay

    def save(self):
        """v确保 Q-table 存储时不报错 """
        os.makedirs(os.path.dirname(self.q_table_path), exist_ok=True)
        with open(self.q_table_path, "w") as f:
            json.dump(self.q_table, f, indent=4)

    def load(self):
        try:
            with open(self.q_table_path, "r") as f:
                self.q_table = json.load(f)
        except FileNotFoundError:
            pass
