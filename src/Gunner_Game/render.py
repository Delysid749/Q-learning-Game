"""
全局渲染文件
"""

import os
import random

import pygame.display

# 获取当前文件的父目录路径
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 子弹的图片路径
BULLET_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "images", "bullet_img", "bullet-background.png")

# 射击手图片路径（随机选取）
GUNNER_IMAGE_DIR = os.path.join(BASE_DIR, "assets", "images", "gunner_img")
# 获取射击手图片文件夹中所有 .png 格式的图片文件
gunner_images = [f for f in os.listdir(GUNNER_IMAGE_DIR) if f.endswith(".png")]
# 随机选取一个射击手图片，如果图片列表为空，则为 None
GUNNER_IMAGE_PATH = os.path.join(GUNNER_IMAGE_DIR, random.choice(gunner_images)) if gunner_images else None

# 障碍（敌人）图片路径（随机选取）
ENEMY_IMAGE_DIR = os.path.join(BASE_DIR, "assets", "images", "enemy_img")

# 初始化 pygame 模块，包括显示和音效
pygame.init()
pygame.mixer.init()

# 游戏音效渲染路径
BE_ATTACKED_PATH = os.path.join(BASE_DIR, "assets", "sounds", "attacked", "be_attacked.mp3")
# 加载被攻击音效
be_attacked_sound = pygame.mixer.Sound(BE_ATTACKED_PATH)
# 游戏失败音效
GAME_FAIL_PATH = os.path.join(BASE_DIR, "assets", "sounds", "game_over", "game-fail.mp3")
game_fail_sound = pygame.mixer.Sound(GAME_FAIL_PATH)
# 得分音效
SCORE_PATH = os.path.join(BASE_DIR, "assets", "sounds", "score", "score-recieved.mp3")
score_sound = pygame.mixer.Sound(SCORE_PATH)


def get_random_enemy_image():
    """ 随机选择一个敌人图片 """
    # 获取敌人图片文件夹中所有 .png 格式的图片文件
    enemy_images = [f for f in os.listdir(ENEMY_IMAGE_DIR) if f.endswith(".png")]
    # 如果有敌人图片，随机选取一张并返回其加载后的图像
    if enemy_images:
        enemy_path = os.path.join(ENEMY_IMAGE_DIR, random.choice(enemy_images))
        enemy_image = pygame.image.load(enemy_path).convert_alpha()
        return enemy_image
    return None  # 如果没有敌人图片，返回 None


# 定义全局颜色
WHITE = (255, 255, 255)  # 白色
RED = (255, 0, 0)  # 红色
BLUE = (0, 0, 255)  # 蓝色
BLACK = (0, 0, 0)  # 黑色

# 设置游戏窗口的宽度和高度
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 700
# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# 渲染游戏结束界面
def game_over_screen(screen, font, score):
    """
    渲染游戏结束画面，显示最终得分，并播放游戏失败音效
    """
    game_fail_sound.play()  # 播放游戏失败音效
    screen.fill(WHITE)  # 填充屏幕背景色为白色

    # 渲染 "GAME OVER" 文本
    game_over_text = font.render("GAME OVER", True, BLACK)
    # 渲染最终得分文本
    final_score_text = font.render(f"Final Score: {score}", True, BLACK)

    # 在屏幕上绘制文本，居中显示
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10))

    pygame.display.update()  # 更新屏幕显示
    pygame.time.delay(2000)  # 暂停 2 秒钟，展示游戏结束画面
    pygame.quit()  # 退出 pygame


# 渲染左上角分数和生命值
def draw_ui(screen, font, score, gunner_lives):
    """
    渲染游戏界面左上角的分数和生命值
    """
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, 70))  # 绘制一个白色矩形区域，用作 UI 背景
    # 渲染分数文本
    score_text = font.render(f"Score: {score}", True, BLACK)
    # 渲染生命值文本
    lives_text = font.render(f"Lives: {gunner_lives}", True, BLACK)

    # 在 UI 区域绘制分数和生命值
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
