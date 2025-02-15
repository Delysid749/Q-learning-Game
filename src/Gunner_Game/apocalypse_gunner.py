import pygame
import random
from Gunner_Game.environment import ApocalypseGunnerEnv

# 初始化 Pygame
pygame.init()

# 游戏窗口设置
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Apocalypse Gunner")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# 文字显示
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# 创建游戏环境
env = ApocalypseGunnerEnv()
state = env.reset()

# **事件监听**
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# **绘制界面**
def draw_objects():
    screen.fill(WHITE)

    # 画出玩家角色
    pygame.draw.rect(screen, BLUE, (env.gunner_x, env.gunner_y, env.gunner_size_x, env.gunner_size_y))

    # 画出子弹
    for bullet in env.bullets_list:
        pygame.draw.rect(screen, RED, (bullet[0], bullet[1], 5, 10))

    # 画出敌人
    for enemy in env.enemy_list:
        pygame.draw.rect(screen, BLACK, (enemy[0], enemy[1], env.gunner_size_x, env.gunner_size_y))

    # 显示分数和生命值
    score_text = font.render(f"Score: {env.score}", True, BLACK)
    lives_text = font.render(f"Lives: {env.gunner_lives}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))

    pygame.display.update()

# **游戏主循环**
running = True
while running:
    handle_events()

    # 获取键盘输入控制
    keys = pygame.key.get_pressed()
    action = None  # 0: 左移, 1: 右移, 2: 开火

    if keys[pygame.K_LEFT]:
        action = 0
    if keys[pygame.K_RIGHT]:
        action = 1
    if keys[pygame.K_SPACE]:
        action = 2

    if action is not None:
        state, reward, done = env.step(action)  # 通过 `environment.py` 控制游戏
        if done:
            running = False

    draw_objects()
    clock.tick(30)

# **游戏结束**
screen.fill(WHITE)
game_over_text = font.render("GAME OVER", True, BLACK)
final_score_text = font.render(f"Final Score: {env.score}", True, BLACK)
screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10))
pygame.display.update()
pygame.time.delay(2000)
pygame.quit()
