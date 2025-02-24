from datetime import time
import numpy as np
import pygame
import random
from Gunner_Game.render import (BLACK, SCREEN_WIDTH, SCREEN_HEIGHT,
                                BULLET_IMAGE_PATH, GUNNER_IMAGE_PATH, get_random_enemy_image,
                                be_attacked_sound, score_sound, game_fail_sound)


class ApocalypseGunnerEnv:
    def __init__(self, is_training=False):
        """ 初始化游戏环境
        :param is_training: 是否用于 AI 训练模式 (AI 训练不需要 Pygame 渲染)
        """

        # AI 训练模式不渲染画面
        self.is_training = is_training

        # 公共参数（尺寸、速度等）即使在训练模式下也需要
        self.gunner_size_x, self.gunner_size_y = 50, 50
        self.gunner_speed = 10
        self.gunner_lives = 1

        self.bullet_size_x, self.bullet_size_y = 25, 30
        self.bullet_velocity = 7

        self.enemy_size_x, self.enemy_size_y = 50, 50
        self.enemy_speed = 2
        self.enemy_spawn_rate = 0.1

        self.MAX_BULLETS = 5

        # 如果不是训练模式，则加载图像和声音
        if not self.is_training:
            # 渲染图像
            self.gunner_image = pygame.image.load(GUNNER_IMAGE_PATH).convert_alpha()
            self.gunner_model = pygame.transform.scale(self.gunner_image, (self.gunner_size_x, self.gunner_size_y))

            self.bullet_image = pygame.image.load(BULLET_IMAGE_PATH).convert_alpha()
            self.bullet_model = pygame.transform.scale(self.bullet_image, (self.bullet_size_x, self.bullet_size_y))

            # 声音也只在非训练模式下加载
            self.score_sound = score_sound
            self.be_attacked_sound = be_attacked_sound
        else:
            # 训练模式下用 None
            self.gunner_image = None
            self.gunner_model = None
            self.bullet_image = None
            self.bullet_model = None

            # 声音也无需加载
            self.score_sound = None
            self.be_attacked_sound = None

        self.reset()

    def reset(self):
        """ 复位游戏，返回初始状态 """
        self.gunner_x = SCREEN_WIDTH // 2 - self.gunner_size_x // 2
        self.gunner_y = SCREEN_HEIGHT - 100
        self.enemy_list = []
        self.bullets_list = []
        self.score = 0
        self.gunner_lives = 1
        self.done = False

        return self.get_state()

    # def get_state(self):
    #     """
    #     状态编码：返回一个三元组 (enemy_speed, xdiff, ydiff)
    #       - enemy_speed：固定的敌人下降速度
    #       - xdiff：最近敌人 x 坐标与射击手 x 坐标的差（正表示敌人在右侧，负表示在左侧）
    #       - ydiff：最近敌人 y 坐标与射击手 y 坐标的差（正表示敌人在下方，负表示在上方）
    #     如果没有敌人，则返回默认远距离值。
    #     """
    #     state_features = []
    #
    #     # 玩家位置（16等分，精度提升60%）
    #     gunner_x_bin = int(self.gunner_x / (SCREEN_WIDTH // 16))
    #     state_features.append(gunner_x_bin)
    #
    #     # 敌人特征编码（最多3个）
    #     enemy_features = []
    #     sorted_enemies = sorted(self.enemy_list, key=lambda e: e[1])[:3]  # 取最近的3个敌人
    #
    #     for enemy in sorted_enemies:
    #         # 相对位置（带方向编码）
    #         dx = (enemy[0] - self.gunner_x) / SCREEN_WIDTH  # 归一化水平差 [-1,1]
    #         dy = (enemy[1] - self.gunner_y) / SCREEN_HEIGHT  # 归一化垂直差 [0,1]
    #         # 离散化水平和垂直距离
    #         dx_bin = int(dx * 10)  # 水平位置分箱（-10到+10）
    #         dy_bin = int(dy * 10)  # 垂直位置分箱（0到+10）
    #
    #         enemy_features.extend([dx_bin, dy_bin])
    #
    #     # 填充不足3个敌人的情况
    #     if len(sorted_enemies) < 3:
    #         enemy_features.extend([0] * 2 * (3 - len(sorted_enemies)))
    #
    #     state_features.extend(enemy_features)
    #
    #     # 子弹特征（增强）：
    #     bullet_status = [
    #         min(len(self.bullets_list), 3),  # 子弹数量
    #         int(any(b[1] < SCREEN_HEIGHT / 2 for b in self.bullets_list)),  # 是否有子弹在屏幕上半部
    #         self.shoot_cooldown // 5  # 冷却时间分箱（每5帧为一档）
    #     ]
    #     state_features.extend(bullet_status)
    #
    #     return tuple(state_features)
    def get_state(self):
        """
        状态编码：返回一个三元组 (enemy_speed, xdiff, ydiff)
          - enemy_speed：固定的敌人下降速度
          - xdiff：最近敌人 x 坐标与射击手 x 坐标的差（正表示敌人在右侧，负表示在左侧）
          - ydiff：最近敌人 y 坐标与射击手 y 坐标的差（正表示敌人在下方，负表示在上方）
        如果没有敌人，则返回默认远距离值。
        """
        enemy_speed = self.enemy_speed
        if self.enemy_list:
            nearest_enemy = min(self.enemy_list, key=lambda e: abs(e[0] - self.gunner_x))
            xdiff = nearest_enemy[0] - self.gunner_x
            ydiff = nearest_enemy[1] - self.gunner_y
        else:
            xdiff = SCREEN_WIDTH
            ydiff = SCREEN_HEIGHT
        return (enemy_speed, xdiff, ydiff)

    def step(self, action):
        """
            修改后的 step 函数，仅接受三个动作：
                0：左移动
                1：右移动
                2：射击开火
        """
        reward = 0
        old_x = self.gunner_x
        # 处理动作
        if action == 0:  # 向左移动
            self.gunner_x = max(0, self.gunner_x - self.gunner_speed)
        elif action == 1:  # 向右移动
            self.gunner_x = min(SCREEN_WIDTH - self.gunner_size_x, self.gunner_x + self.gunner_speed)
        elif action == 2:  # 射击开火
            if len(self.bullets_list) < self.MAX_BULLETS:
                bullet_x = self.gunner_x + self.gunner_size_x // 2 - self.bullet_size_x // 2
                bullet_y = self.gunner_y
                self.bullets_list.append([bullet_x, bullet_y])

        # 更新子弹和敌人的状态
        self.update_objects()

        # 奖励机制
        reward += self.get_reward(old_x=old_x, action=action)

        # 判断是否结束
        if self.gunner_lives <= 0:
            self.done = True

        return self.get_state(), reward, self.done

    def check_bullet_enemy_collision(self):
        """
        检测子弹与敌人碰撞
        返回列表，每个元素为 (bullet, enemy) 的元组
        """
        collided_pairs = []
        for bullet in self.bullets_list:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], self.bullet_size_x, self.bullet_size_y)
            for enemy in self.enemy_list:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], self.enemy_size_x, self.enemy_size_y)
                if bullet_rect.colliderect(enemy_rect):
                    collided_pairs.append((bullet, enemy))
        return collided_pairs

    def get_reward(self,old_x=None, action=None):
        """ 计算奖励函数 """
        reward = 0
        collided_pairs = self.check_bullet_enemy_collision()
        bullets_to_remove = []
        enemies_to_remove = set()

        # 命中敌人：奖励 +100 分
        for bullet, enemy in collided_pairs:
            bullets_to_remove.append(bullet)
            enemies_to_remove.add(tuple(enemy))
            reward += 100
            self.score += 10
            if self.score_sound:
                self.score_sound.play()

        # 移除已命中对象
        self.bullets_list = [b for b in self.bullets_list if b not in bullets_to_remove]
        self.enemy_list = [e for e in self.enemy_list if tuple(e) not in enemies_to_remove]

        # 检测与敌人碰撞（降低生命并给予较大惩罚）
        gunner_rect = pygame.Rect(self.gunner_x, self.gunner_y, self.gunner_size_x, self.gunner_size_y)
        for enemy in self.enemy_list:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], self.enemy_size_x, self.enemy_size_y)
            if gunner_rect.colliderect(enemy_rect):
                if old_x is not None and action is not None and self.enemy_list:
                    nearest_enemy = min(self.enemy_list, key=lambda e: abs(e[0] - old_x))
                    enemy_x = nearest_enemy[0]

                    move_left_toward_enemy = (enemy_x < old_x) and (action == 0)
                    move_right_toward_enemy = (enemy_x > old_x) and (action == 1)
                    if move_left_toward_enemy or move_right_toward_enemy:
                        reward = -1000
                    else:
                        reward -= 1000
                if self.be_attacked_sound:
                    self.be_attacked_sound.play()
                self.gunner_lives -= 1
                break
        return reward

    def spawn_enemy(self):
        enemy_x = random.randint(0, SCREEN_WIDTH - self.enemy_size_x)
        enemy_img = get_random_enemy_image()
        enemy_img = pygame.transform.scale(enemy_img, (self.enemy_size_x, self.enemy_size_y))
        # 新生成的敌人 y 坐标从0开始
        self.enemy_list.append([enemy_x, 0, enemy_img])

    def update_objects(self):
        # 更新子弹位置
        new_bullets = []
        for b in self.bullets_list:
            new_y = b[1] - self.bullet_velocity
            if new_y > 0:
                new_bullets.append([b[0], new_y])
        self.bullets_list = new_bullets

        # 更新敌人位置
        self.enemy_list = [[e[0], e[1] + self.enemy_speed, e[2]] for e in self.enemy_list if e[1] < SCREEN_HEIGHT]

        # 固定规则：一个敌人一个敌人生成
        if len(self.enemy_list) == 0:
            # 如果没有敌人，直接生成一个
            self.spawn_enemy()
        elif len(self.enemy_list) == 1:
            # 如果只有一个敌人，检查它是否滑过屏幕1/4高度
            if self.enemy_list[0][1] > SCREEN_HEIGHT // 4:
                self.spawn_enemy()

    def render(self, screen):
        """ 绘制游戏对象 """
        screen.blit(self.gunner_model, (self.gunner_x, self.gunner_y))
        for bullet in self.bullets_list:
            screen.blit(self.bullet_model, (bullet[0], bullet[1]))
        for enemy in self.enemy_list:
            screen.blit(enemy[2], (enemy[0], enemy[1]))
