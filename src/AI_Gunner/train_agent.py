import os
import random
import json
import matplotlib.pyplot as plt

from Gunner_Game.environment import ApocalypseGunnerEnv
from AI_Gunner.agent import QLearningAgent
from logs_config.log_config import train_logger

def train(num_episodes=100):
    env = ApocalypseGunnerEnv(is_training=True)
    agent = QLearningAgent(state_size=len(env.get_state()), action_size=3)
    agent.load()

    # 用于可视化的数据
    rewards_history = []      # 每回合总奖励
    epsilon_history = []      # 每回合 epsilon
    alpha_history = []        # 每回合 alpha
    hits_history = []         # 每回合击落敌人数量
    collisions_history = []   # 每回合是否发生碰撞(1=是,0=否)
    MAX_STEPS = 10000
    train_logger.info("训练开始")

    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0
        done = False
        step_count = 0

        # 用来统计击落敌人的增量
        initial_score = env.score

        while not done and step_count < MAX_STEPS:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)

            agent.store_move(state, action)

            state = next_state
            total_reward += reward
            step_count += 1

            if step_count >= MAX_STEPS:
                done = True

        # 回合结束后更新 Q 值
        agent.update_scores(total_reward, state)
        agent.save()  # 保存训练后的 Q 表

        # 记录可视化数据
        rewards_history.append(total_reward)
        epsilon_history.append(agent.epsilon)
        alpha_history.append(agent.alpha)

        hits_this_episode = env.score - initial_score
        hits_history.append(hits_this_episode)

        collision_flag = 1 if env.gunner_lives <= 0 else 0
        collisions_history.append(collision_flag)

        train_logger.info(
            f"回合 {episode + 1}: 总奖励 = {total_reward:.2f}, "
            f"步数 = {step_count}, 探索率 = {agent.epsilon:.4f}, 学习率 = {agent.alpha:.4f}"
        )
        print(f"Episode {episode + 1}: Reward={total_reward}, "
              f"Epsilon={agent.epsilon:.4f}, Alpha={agent.alpha:.4f}")

        # 衰减 eps/alpha
        agent.decay_parameters()

    # 训练结束后再保存一次
    agent.save()
    train_logger.info("训练结束")

    # ===== 调用画图函数，把图表存到 data/train_result 中 =====
    plot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'train_result'))
    os.makedirs(plot_dir, exist_ok=True)

    plot_reward_vs_episode(rewards_history, os.path.join(plot_dir, "reward_vs_episode.png"))
    plot_epsilon_alpha(epsilon_history, alpha_history, os.path.join(plot_dir, "epsilon_alpha.png"))
    plot_hits_collisions(hits_history, collisions_history, os.path.join(plot_dir, "hits_collisions.png"))


def plot_reward_vs_episode(rewards_history, save_path):
    """ 绘制回合总奖励随训练轮次的变化图，并保存 """
    plt.figure()
    plt.plot(rewards_history, label="Reward", color="blue")
    plt.title("Reward vs. Episode")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.legend()
    plt.savefig(save_path)
    plt.close()  # 关闭图像，释放资源


def plot_epsilon_alpha(epsilon_history, alpha_history, save_path):
    """ 绘制 epsilon / alpha 随训练轮次衰减曲线，并保存 """
    episodes = range(1, len(epsilon_history) + 1)
    plt.figure()
    plt.plot(episodes, epsilon_history, label="Epsilon", color="orange")
    plt.plot(episodes, alpha_history, label="Alpha", color="green")
    plt.title("Epsilon / Alpha Decay")
    plt.xlabel("Episode")
    plt.ylabel("Value")
    plt.legend()
    plt.savefig(save_path)
    plt.close()


def plot_hits_collisions(hits_history, collisions_history, save_path):
    """
    绘制击中敌人次数 vs. 碰撞情况:
    - hits_history: 每回合击中的敌人数量
    - collisions_history: 每回合是否碰撞(1/0)
    """
    episodes = range(1, len(hits_history) + 1)
    plt.figure()
    plt.plot(episodes, hits_history, label="Hits", color="blue")
    plt.plot(episodes, collisions_history, label="Collision(1/0)", color="red")
    plt.title("Hits vs. Collisions per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Count")
    plt.legend()
    plt.savefig(save_path)
    plt.close()

