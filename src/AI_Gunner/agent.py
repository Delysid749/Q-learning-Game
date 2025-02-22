# agent.py
import os
import json
import random


class QLearningAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.alpha = 0.7  # 初始学习率
        self.gamma = 0.95  # 折扣因子
        self.epsilon = 0.995  # 初始探索率
        self.epsilon_decay = 0.999
        self.epsilon_min = 0.01

        self.action_dist = {0: 0, 1: 0, 2: 0, 3: 0}

        # 动态学习率参数
        self.alpha_decay = 0.9995
        self.alpha_min = 0.1

        self.q_table = {}
        self.q_table_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'q_value.json')

    def decay_parameters(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.alpha = max(self.alpha_min, self.alpha * self.alpha_decay)

    def get_q(self, state, action):
        state = str(state)
        return self.q_table.get(state, {}).get(action, 0.0)

    def update_q(self, state, action, reward, next_state):
        state = str(state)
        next_state = str(next_state)
        max_next_q = max(self.q_table.get(next_state, {}).values(), default=0)
        old_q = self.get_q(state, action)
        new_q = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)
        self.q_table.setdefault(state, {})[action] = new_q

    def choose_action(self, state):
        state = str(state)
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        else:
            actions = self.q_table.get(state, {})
            if actions:
                action = max(actions, key=actions.get)
            else:
                return 0
        # 更新动作分布
        self.action_dist[action] += 1
        return action

    def save(self):
        os.makedirs(os.path.dirname(self.q_table_path), exist_ok=True)
        with open(self.q_table_path, "w") as f:
            json.dump(self.q_table, f, indent=4)

    def load(self):
        try:
            with open(self.q_table_path, "r") as f:
                self.q_table = json.load(f)
        except FileNotFoundError:
            pass
