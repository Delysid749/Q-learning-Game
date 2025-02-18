import pygame
import random
from Gunner_Game.environment import ApocalypseGunnerEnv
from render import game_over_screen, draw_ui, WHITE, BLACK, RED, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT, screen, BULLET_IMAGE_PATH

# 初始化 Pygame
pygame.init()

# 定义文字
font = pygame.font.Font(None, 36)

# 游戏窗口设置标题
pygame.display.set_caption("Apocalypse Gunner")

clock = pygame.time.Clock()

# **创建游戏环境（玩家模式，不传 is_training，默认渲染画面）**
env = ApocalypseGunnerEnv()
state = env.reset()


# **事件监听**
def handle_events():
    action = "NO_ACTION"  # 默认不执行任何操作
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                action = "LEFT"
            elif event.key == pygame.K_RIGHT:
                action = "RIGHT"
            elif event.key == pygame.K_SPACE:
                action = "SHOOT"
    return action


# **绘制界面**
def draw_objects():
    screen.fill(WHITE)

    # 画出玩家角色
    screen.blit(env.gunner_model,(env.gunner_x,env.gunner_y))


    # 画出子弹
    for bullet in env.bullets_list:
        screen.blit(env.bullet_model, (bullet[0], bullet[1]))

    # 画出敌人
    for enemy in env.enemy_list:
        screen.blit(enemy[2],(enemy[0],enemy[1]))

    # 显示分数和生命值
    draw_ui(screen,font, env.score, env.gunner_lives)

    pygame.display.update()


# **游戏主循环**
done = False
while not done:
    action = handle_events()

    # **无论是否有输入，都执行环境更新**
    state, reward, done = env.step(action)

    draw_objects()
    # **只有在玩家模式下，才调用 render()**
    env.render(screen)

    clock.tick(60)  # 控制帧率

# **游戏结束**
game_over_screen(screen,font, env.score)
