import os
from Gunner_Game.environment import ApocalypseGunnerEnv
from AI_Gunner.agent import QLearningAgent
from logs_config.log_config import train_logger


def train(num_episodes=1000):
    env = ApocalypseGunnerEnv(is_training=True)
    agent = QLearningAgent(state_size=len(env.get_state()), action_size=3)
    agent.load()

    train_logger.info("训练开始")
    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0
        done = False

        MAX_STEPS = 10000  # 每个回合最大步数
        step_count = 0

        while not done and step_count < MAX_STEPS:
            # 选择动作
            action = agent.choose_action(state)

            # 执行动作并获得下一状态和奖励
            next_state, reward, done = env.step(action)

            # 存储状态-动作对
            agent.store_move(state, action)

            state = next_state
            total_reward += reward
            step_count += 1

            # 达到最大步数时结束回合
            if step_count >= MAX_STEPS:
                done = True

        # 回合结束后更新 Q 值并保存
        agent.update_scores(total_reward, state)
        agent.save()
        train_logger.info(
            f"回合 {episode + 1}: 总奖励 = {total_reward:.2f}, 步数 = {step_count}, 探索率 = {agent.epsilon:.4f}")
        print(f"Episode {episode + 1}: Reward: {total_reward}, Epsilon: {agent.epsilon:.4f}")
        agent.decay_parameters()

    agent.save()
    train_logger.info("训练结束")

