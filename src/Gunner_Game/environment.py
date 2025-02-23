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
        # 渲染射击手
        self.gunner_size_x, self.gunner_size_y = 50, 50
        self.gunner_image = pygame.image.load(GUNNER_IMAGE_PATH).convert_alpha()
        self.gunner_model = pygame.transform.scale(self.gunner_image, (self.gunner_size_x, self.gunner_size_y))
        self.gunner_speed = 10
        self.gunner_lives = 1

        # 渲染子弹
        self.bullet_image = pygame.image.load(BULLET_IMAGE_PATH).convert_alpha()
        self.bullet_size_x, self.bullet_size_y = 25, 30
        self.bullet_model = pygame.transform.scale(self.bullet_image, (self.bullet_size_x, self.bullet_size_y))
        self.bullet_velocity = 7

        # 渲染障碍（敌人）
        self.enemy_size_x, self.enemy_size_y = 50, 50
        self.enemy_speed = 2
        self.difficulty_level = 1  # 初始难度等级
        self.enemy_spawn_rate = 0.05  # 初始敌人生成率

        # 最大敌人和子弹数量
        self.MAX_ENEMIES = 8
        self.MAX_BULLETS = 5

        # 初始化速度（例如，默认为0）
        self.gunner_velocity_x = 0
        self.gunner_velocity_y = 0

        # 用于存储状态-动作对
        self.moves = []

        # 初始化 Q 值表
        self.q_table = {}
        self.alpha = 0.7  # 学习率
        self.gamma = 0.95  # 折扣因子

        # AI 训练模式不渲染画面
        self.is_training = is_training
        self.reset()

        self.spawn_interval = 1500  # 初始敌人生成间隔（毫秒）
        self.last_spawn_time = pygame.time.get_ticks()  # 记录上次敌人生成的时间

    def reset(self):
        """ 复位游戏，返回初始状态 """
        self.gunner_x = SCREEN_WIDTH // 2 - self.gunner_size_x // 2
        self.gunner_y = SCREEN_HEIGHT - 100
        self.enemy_list = []
        self.bullets_list = []
        self.score = 0
        self.gunner_lives = 1
        self.done = False
        self.enemy_spawn_rate = 0.1 * self.difficulty_level  # 随难度增加的生成频率
        self.spawn_interval = 1500  # 初始生成间隔（毫秒）
        self.last_spawn_time = pygame.time.get_ticks()  # 记录开始时间

        # 新增：射击冷却计数器和无效射击标志
        self.shoot_cooldown = 0

        self.moves = []  # 清空历史记录
        return self.get_state()

    def get_state(self):
        """增强版状态编码：简化为玩家和敌人的位置差以及速度"""
        state_features = []

        # 玩家位置（16等分，精度提升60%）
        gunner_x_bin = int(self.gunner_x / (SCREEN_WIDTH // 16))
        state_features.append(gunner_x_bin)

        # 敌人特征编码（最多3个）
        enemy_features = []
        sorted_enemies = sorted(self.enemy_list, key=lambda e: e[1])[:3]  # 取最近的3个敌人

        for enemy in sorted_enemies:
            # 相对位置（带方向编码）
            dx = (enemy[0] - self.gunner_x) / SCREEN_WIDTH  # 归一化水平差 [-1,1]
            dy = (enemy[1] - self.gunner_y) / SCREEN_HEIGHT  # 归一化垂直差 [0,1]
            # 离散化水平和垂直距离
            dx_bin = int(dx * 10)  # 水平位置分箱（-10到+10）
            dy_bin = int(dy * 10)  # 垂直位置分箱（0到+10）

            enemy_features.extend([dx_bin, dy_bin])

        # 填充不足3个敌人的情况
        if len(sorted_enemies) < 3:
            enemy_features.extend([0] * 2 * (3 - len(sorted_enemies)))

        state_features.extend(enemy_features)

        # 子弹特征（增强）：
        bullet_status = [
            min(len(self.bullets_list), 3),  # 子弹数量
            int(any(b[1] < SCREEN_HEIGHT / 2 for b in self.bullets_list)),  # 是否有子弹在屏幕上半部
            self.shoot_cooldown // 5  # 冷却时间分箱（每5帧为一档）
        ]
        state_features.extend(bullet_status)

        return tuple(state_features)

    def step(self, action):
        reward = 0
        SHOOT_COOLDOWN = 15  # 射击冷却帧数，约0.25秒（60FPS下15帧）
        shoot_attempt = False

        # 解析动作策略
        if action == 0:  # 左移 + 射击
            self.gunner_x = max(0, self.gunner_x - self.gunner_speed)
            shoot_attempt = True
        elif action == 1:  # 右移 + 射击
            self.gunner_x = min(SCREEN_WIDTH - self.gunner_size_x, self.gunner_x + self.gunner_speed)
            shoot_attempt = True
        elif action == 2:  # 保持 + 射击
            shoot_attempt = True
        elif action == 3:  # 仅移动
            if self.enemy_list:
                nearest_x = sorted(self.enemy_list, key=lambda e: e[1])[0][0]
                if self.gunner_x < nearest_x - 10:
                    self.gunner_x += self.gunner_speed
                elif self.gunner_x > nearest_x + 10:
                    self.gunner_x -= self.gunner_speed

        # 初始化 Q 值
        state = self.get_state()
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in range(4)}  # 给所有可能的动作初始化 Q 值

        # 处理射击逻辑
        if shoot_attempt and self.shoot_cooldown <= 0 and len(self.bullets_list) < self.MAX_BULLETS:
            bullet_x = self.gunner_x + self.gunner_size_x // 2 - self.bullet_size_x // 2
            bullet_y = self.gunner_y
            self.bullets_list.append([bullet_x, bullet_y])
            self.shoot_cooldown = SHOOT_COOLDOWN

        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)

        # 更新子弹和敌人的状态
        self.update_objects()

        # 奖励机制
        reward += self.get_reward()

        # 判断是否结束
        if self.gunner_lives <= 0:
            self.done = True
            self.update_scores()  # 回合结束时更新 Q 值

        self.moves.append((state, action))

        return self.get_state(), reward, self.done

    def get_q(self, state, action):
        state = str(state)  # 将状态转换为字符串
        return self.q_table.get(state, {}).get(action, 0.0)

    def update_scores(self):
        """ 更新 Q 值 """
        for state, action in reversed(self.moves):
            reward = self.get_reward()
            max_next_q = max(self.q_table.get(state, {}).values(), default=0)
            old_q = self.get_q(state, action)
            new_q = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)
            self.q_table.setdefault(state, {})[action] = new_q
        self.moves = []  # 清空历史记录


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

    def get_reward(self):
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
            score_sound.play()

        # 移除已命中对象
        self.bullets_list = [b for b in self.bullets_list if b not in bullets_to_remove]
        self.enemy_list = [e for e in self.enemy_list if tuple(e) not in enemies_to_remove]

        # 生存奖励
        reward += 0.01

        # 检测与敌人碰撞（降低生命并给予较大惩罚）
        gunner_rect = pygame.Rect(self.gunner_x, self.gunner_y, self.gunner_size_x, self.gunner_size_y)
        enemies_collided = []
        for enemy in self.enemy_list:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], self.enemy_size_x, self.enemy_size_y)
            if gunner_rect.colliderect(enemy_rect):
                be_attacked_sound.play()
                self.gunner_lives -= 1
                enemies_collided.append(enemy)
                reward -= 100
        self.enemy_list = [e for e in self.enemy_list if e not in enemies_collided]

        return reward

    def increase_difficulty(self):
        """ 随着训练进度提升难度 """
        self.difficulty_level += 1
        self.enemy_spawn_rate = min(1.0, self.enemy_spawn_rate + 0.05)  # 最大生成概率为1.0
        self.enemy_speed += 1  # 敌人速度逐渐增加

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_interval:
            enemy_x = random.randint(0, SCREEN_WIDTH - self.enemy_size_x)
            enemy_img = get_random_enemy_image()
            enemy_img = pygame.transform.scale(enemy_img, (self.enemy_size_x, self.enemy_size_y))
            self.enemy_list.append([enemy_x, 0, enemy_img])
            self.last_spawn_time = current_time
            # 随着游戏时间增加，减少生成间隔，增加敌人密度
            self.spawn_interval = max(200, self.spawn_interval - 20)

    def update_objects(self):
        # 更新子弹位置
        new_bullets = []
        for b in self.bullets_list:
            new_y = b[1] - self.bullet_velocity
            if new_y > 0:
                new_bullets.append([b[0], new_y])
        self.bullets_list = new_bullets

        # 更新敌人位置并生成新敌人
        self.enemy_list = [[e[0], e[1] + self.enemy_speed, e[2]] for e in self.enemy_list if e[1] < SCREEN_HEIGHT]
        self.spawn_enemy()

    def render(self, screen):
        """ 绘制游戏对象 """
        screen.blit(self.gunner_model, (self.gunner_x, self.gunner_y))
        for bullet in self.bullets_list:
            screen.blit(self.bullet_model, (bullet[0], bullet[1]))
        for enemy in self.enemy_list:
            screen.blit(enemy[2], (enemy[0], enemy[1]))
