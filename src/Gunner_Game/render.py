import os
import random

import pygame.display

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 子弹的图片路径
BULLET_IMAGE_PATH = os.path.join(BASE_DIR,"assets","images","bullet_img","bullet-background.png")

# 射击手图片路径（随机选取）
GUNNER_IMAGE_DIR = os.path.join(BASE_DIR,"assets","images","gunner_img")
gunner_images = [f for f in os.listdir(GUNNER_IMAGE_DIR) if f.endswith(".png")]
GUNNER_IMAGE_PATH = os.path.join(GUNNER_IMAGE_DIR,random.choice(gunner_images)) if gunner_images else None

# 障碍图片路径（随机选取）
ENEMY_IMAGE_DIR = os.path.join(BASE_DIR,"assets","images","enemy_img")
def get_random_enemy_image():
    """ 随机选择一个敌人图片 """
    enemy_images = [f for f in os.listdir(ENEMY_IMAGE_DIR) if f.endswith(".png")]
    if enemy_images:
        enemy_path = os.path.join(ENEMY_IMAGE_DIR, random.choice(enemy_images))
        enemy_image = pygame.image.load(enemy_path).convert_alpha()
        return enemy_image
    return None


# enemy_images = [f for f in os.listdir(ENEMY_IMAGE_DIR) if f.endswith(".png")]
# ENEMY_IMAGE_PATH = os.path.join(ENEMY_IMAGE_DIR,random.choice(enemy_images)) if enemy_images else None

# 定义全局颜色
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# 游戏窗口设置
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# 渲染游戏结束
def game_over_screen(screen, font, score):
    # 游戏结束
    screen.fill(WHITE)
    game_over_text = font.render("GAME OVER", True, BLACK)
    final_score_text = font.render(f"Final Score: {score}", True, BLACK)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10))

    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()


# 渲染左上角分数、生命值显示
def draw_ui(screen, font, score, gunner_lives):
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, 70))
    score_text = font.render(f"Score: {score}", True, BLACK)
    lives_text = font.render(f"Lives: {gunner_lives}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
