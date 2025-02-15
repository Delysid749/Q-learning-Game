from environment import ApocalypseGunnerEnv
import numpy as np

# 创建游戏环境
env = ApocalypseGunnerEnv()

# 复位游戏，获取初始状态
state = env.reset()
print("初始状态:", state)

done = False
total_reward = 0
step_count = 0

while not done and step_count < 20:  # 限制步数，防止无限循环
    action = np.random.choice([0, 1, 2])  # AI 随机执行 左 (0) / 右 (1) / 开火 (2)
    next_state, reward, done = env.step(action)

    total_reward += reward
    step_count += 1
    print(f"Step {step_count}: Action {action}, Reward {reward}, Total Reward {total_reward}")

print("✅ 测试完成，游戏结束")
