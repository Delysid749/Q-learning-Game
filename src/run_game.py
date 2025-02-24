import pygame
from Gunner_Game.environment import ApocalypseGunnerEnv
from AI_Gunner.agent import QLearningAgent
from logs_config.log_config import game_logger
from Gunner_Game.render import game_over_screen, draw_ui, WHITE, screen

# 初始化 Pygame
pygame.init()

font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

# 载入环境 & AI 代理
env = ApocalypseGunnerEnv(is_training=False)
agent = QLearningAgent(state_size=len(env.get_state()), action_size=3)
agent.load()  # 加载 Q-table

# AI 控制游戏
done = False
state = str(tuple(env.reset()))

while not done:
    pygame.event.pump()  # 处理 Pygame 事件，防止窗口无响应

    screen.fill(WHITE)
    # 绘制分数和生命值
    draw_ui(screen, font, env.score, env.gunner_lives)

    # 让 AI 选择最佳动作
    action = agent.choose_action(state)

    # 执行动作 & 更新环境
    state, reward, done = env.step(action)

    env.render(screen)

    pygame.display.update()

    clock.tick(60)  # 控制帧率

game_over_screen(screen, font, env.score)
