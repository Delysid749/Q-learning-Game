import logging
import os.path

from Gunner_Game.environment import ApocalypseGunnerEnv
from AI_Gunner.agent import QLearningAgent
import numpy as np
from logs_config.log_config import train_logger


def train(num_episodes=5000):
    """ 训练 AI 代理 """
    env = ApocalypseGunnerEnv()
    agent = QLearningAgent(state_size=len(env.get_state()), action_size=3)

    for episode in range(num_episodes):
        state = str(tuple(env.reset()))
        total_reward = 0

        for step in range(200):  # 限制每个回合最多 200 步
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            next_state = tuple(next_state)

            # 更新 Q-table
            agent.update_q(state, action, reward, next_state)
            state = next_state
            total_reward += reward

            if done:
                break

        agent.decay_epsilon()  # 逐步减少探索率

        # 记录训练日志
        train_logger.info(f"Episode {episode}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.4f}")

        if episode % 100 == 0:
            print(f"Episode {episode}, Total Reward: {total_reward}")

    agent.save()
    print("训练完成，Q-table 已保存！")

# 只有直接运行 train_agent.py 时才会执行
if __name__ == "__main__":
    train()
