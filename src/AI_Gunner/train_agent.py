import logging
import os.path

from matplotlib import pyplot as plt

from Gunner_Game.environment import ApocalypseGunnerEnv
from AI_Gunner.agent import QLearningAgent
import numpy as np
from logs_config.log_config import train_logger

RESULTS_DIR = "../data/train_result"
def train(num_episodes=5000):
    """ 训练 AI 代理 """
    env = ApocalypseGunnerEnv(is_training=True)
    agent = QLearningAgent(state_size=len(env.get_state()), action_size=3)

    reward_history = []

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
        reward_history.append(total_reward)
        # 记录训练日志
        if episode % 1000 == 0:
            print(f"Episode {episode}, Total Reward: {total_reward}")
            train_logger.info(f"Episode {episode}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.4f}")

    agent.save()
    print("训练完成，Q-table 已保存！")
    plot_rewards(reward_history)

def plot_rewards(reward_history):
    """
    绘制并保存奖励曲线
    """
    plt.figure(figsize=(10, 5))
    plt.plot(reward_history, label='Total Reward per Episode', color='blue', linewidth=1.5)
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Training Progress - Reward Curve')
    plt.legend()
    plt.grid()

    # 保存图片到 `train_result` 文件夹
    reward_plot_path = os.path.join(RESULTS_DIR, "reward_curve.png")
    plt.savefig(reward_plot_path, dpi=300)
    print(f"奖励曲线已保存到: {reward_plot_path}")

    plt.close()  # 关闭图像，避免 GUI 显示

