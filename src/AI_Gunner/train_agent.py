import datetime
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from Gunner_Game.environment import ApocalypseGunnerEnv
from AI_Gunner.agent import QLearningAgent

RESULTS_DIR = os.path.join("..", "data", "train_result")


def train(num_episodes=2000, interval=100):
    env = ApocalypseGunnerEnv(is_training=True)
    agent = QLearningAgent(state_size=len(env.get_state()), action_size=4)
    agent.load()  # 加载已有的 Q-table（如果存在）

    # 初始化监控指标
    metrics = {
        'hit_rate': [],
        'avg_distance': [],
        'shoot_efficiency': [],
        'episode_rewards': []
    }

    # 状态覆盖率监控
    unique_states = set()

    # 动作分布监控
    action_dist = {0: 0, 1: 0, 2: 0, 3: 0}

    for episode in range(num_episodes):
        print(f"Starting episode {episode + 1}...")
        state = env.reset()
        total_reward = 0
        done = False

        # 指标统计变量
        hits = 0
        shots = 0
        distances = []

        while not done:
            prev_bullet_count = len(env.bullets_list)

            # 选择动作
            action = agent.choose_action(state)

            # 更新动作分布
            action_dist[int(action)] += 1

            # 执行动作
            next_state, reward, done = env.step(action)

            # 检查是否产生了新的子弹（即执行了射击操作）
            new_bullet_count = len(env.bullets_list)
            if new_bullet_count > prev_bullet_count:
                shots += 1

            if reward >= 100:
                hits += reward // 100  # 每100分代表一次命中

            if env.enemy_list:
                nearest = min(env.enemy_list, key=lambda e: abs(e[0] - env.gunner_x))
                distances.append(abs(nearest[0] - env.gunner_x))

            # 存储状态-动作对
            agent.store_move(state, action)

            state = next_state
            total_reward += reward

        # 在每回合结束后更新 Q 值
        agent.update_scores(total_reward, state)
        agent.save()  # 保存Q值
        print(f"Episode {episode + 1}: Q-values updated and saved.")

        hit_rate = hits / shots if shots > 0 else 0
        avg_distance = np.mean(distances) if distances else 0
        shoot_efficiency = hits / shots if shots > 0 else 0

        metrics['hit_rate'].append(hit_rate)
        metrics['avg_distance'].append(avg_distance)
        metrics['shoot_efficiency'].append(shoot_efficiency)
        metrics['episode_rewards'].append(total_reward)

        print(f"Episode {episode}, Reward: {total_reward}, Epsilon: {agent.epsilon:.4f}, "
              f"Hit Rate: {hit_rate:.2f}, Avg Distance: {avg_distance:.2f}")

        # 每100轮输出一次状态覆盖率和动作分布
        if episode % 100 == 0:
            print(f"Unique states: {len(unique_states)}")
            print(f"Action distribution: {action_dist}")

        # 难度提升
        # if episode % interval == 0:
        #     env.increase_difficulty()

    agent.save()
    plot_metrics(metrics)


def plot_metrics(metrics):
    episodes = range(len(metrics['episode_rewards']))

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    plt.plot(episodes, metrics['episode_rewards'], color='blue', linewidth=1.5)
    plt.title("Episode Rewards")
    plt.xlabel("Episode")
    plt.ylabel("Reward")

    plt.subplot(2, 2, 2)
    plt.plot(episodes, metrics['hit_rate'], color='green', linewidth=1.5)
    plt.title("Hit Rate")
    plt.xlabel("Episode")
    plt.ylabel("Hit Rate")

    plt.subplot(2, 2, 3)
    plt.plot(episodes, metrics['avg_distance'], color='red', linewidth=1.5)
    plt.title("Average Distance")
    plt.xlabel("Episode")
    plt.ylabel("Avg Distance")

    plt.subplot(2, 2, 4)
    plt.plot(episodes, metrics['shoot_efficiency'], color='purple', linewidth=1.5)
    plt.title("Shooting Efficiency")
    plt.xlabel("Episode")
    plt.ylabel("Efficiency")

    plt.tight_layout()
    timestamp = datetime.datetime.now().strftime("%m_%H%M")
    plot_path = os.path.join(RESULTS_DIR, f"metrics_{timestamp}.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"训练指标图已保存到: {plot_path}")
