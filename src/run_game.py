import pygame
from Gunner_Game.environment import ApocalypseGunnerEnv
from AI_Gunner.agent import QLearningAgent
from logs_config.log_config import game_logger

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((500, 700))  # 创建游戏窗口
clock = pygame.time.Clock()

# 载入环境 & AI 代理
env = ApocalypseGunnerEnv()
agent = QLearningAgent(state_size=len(env.get_state()), action_size=3)
agent.load()  # 加载 Q-table

# AI 控制游戏
done = False
state = tuple(env.reset())

while not done:
    pygame.event.pump()  # 处理 Pygame 事件，防止窗口无响应

    # 让 AI 选择最佳动作
    action = agent.choose_action(state)

    # 执行动作 & 更新环境
    state, reward, done = env.step(action)


    # **修正**：正确传入 `screen`
    env.render(screen)

    clock.tick(60)  # 控制帧率

pygame.quit()
