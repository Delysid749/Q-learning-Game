import numpy as np
import pygame
import random
from Gunner_Game.render import (BLACK, SCREEN_WIDTH, SCREEN_HEIGHT,
                                BULLET_IMAGE_PATH, GUNNER_IMAGE_PATH, get_random_enemy_image,be_attacked_sound,score_sound,game_fail_sound)


class ApocalypseGunnerEnv:
    def __init__(self, is_training=False):
        """ 初始化游戏环境
        :param is_training: 是否用于 AI 训练模式 (AI 训练不需要 Pygame 渲染)
        """
        # 渲染射击手
        self.gunner_size_x, self.gunner_size_y = 50, 50
        self.gunner_image = pygame.image.load(GUNNER_IMAGE_PATH).convert_alpha()
        self.gunner_model = pygame.transform.scale(self.gunner_image, (self.gunner_size_x, self.gunner_size_y))
        self.gunner_speed = 5

        # 渲染子弹
        self.bullet_image = pygame.image.load(BULLET_IMAGE_PATH).convert_alpha()
        self.bullet_size_x, self.bullet_size_y = 25, 30
        self.bullet_model = pygame.transform.scale(self.bullet_image, (self.bullet_size_x, self.bullet_size_y))
        self.bullet_velocity = 7

        # 渲染障碍
        self.enemy_size_x, self.enemy_size_y = 50, 50
        self.enemy_speed = 3

        # 最大障碍、子弹
        self.MAX_ENEMIES = 5
        self.MAX_BULLETS = 3

        # AI 训练模式不渲染画面
        self.is_training = is_training
        self.reset()



    def reset(self):
        """ 复位游戏，返回初始状态 """
        self.gunner_x = SCREEN_WIDTH // 2 - self.gunner_size_x // 2
        self.gunner_y = SCREEN_HEIGHT - 100
        self.enemy_list = []
        self.bullets_list = []
        self.score = 0
        self.gunner_lives = 3
        self.done = False
        return self.get_state()

    def get_state(self):
        """ 获取游戏状态 (归一化处理) """
        gunner_state = [self.gunner_x / SCREEN_WIDTH, self.gunner_y / SCREEN_HEIGHT]

        # 敌人状态：若不足 MAX_ENEMIES，后面补零；若多余则截取前 MAX_ENEMIES 个
        enemies_state = []
        for enemy in self.enemy_list[:self.MAX_ENEMIES]:
            enemies_state.extend([enemy[0] / SCREEN_WIDTH, enemy[1] / SCREEN_HEIGHT])
        enemies_state += [0] * (2 * (self.MAX_ENEMIES - len(self.enemy_list)))

        # 子弹状态
        bullets_state = []
        for bullet in self.bullets_list[:self.MAX_BULLETS]:
            bullets_state.extend([bullet[0] / SCREEN_WIDTH, bullet[1] / SCREEN_HEIGHT])
        bullets_state += [0] * (2 * (self.MAX_BULLETS - len(self.bullets_list)))

        return np.array(gunner_state + enemies_state + bullets_state)

    def step(self, action):
        """ 执行动作并返回 (新状态, 奖励, 是否结束)
        :param action: int (0=LEFT, 1=RIGHT, 2=SHOOT) 或 str ('LEFT', 'RIGHT', 'SHOOT')
        """
        reward = 0

        # **兼容 AI 训练和玩家模式**
        if isinstance(action, str):
            action_map = {"LEFT": 0, "RIGHT": 1, "SHOOT": 2, "NO_ACTION": -1}
            action = action_map.get(action, -1)

        # 角色移动
        if action == 0:  # 左移
            self.gunner_x = max(0, self.gunner_x - self.gunner_speed)
        elif action == 1:  # 右移
            self.gunner_x = min(SCREEN_WIDTH - self.gunner_size_x, self.gunner_x + self.gunner_speed)
        elif action == 2:  # 开火
            self.bullets_list.append([self.gunner_x + self.gunner_size_x // 2 - self.bullet_size_x // 2, self.gunner_y])

        # **即使无输入，也要更新游戏状态**
        self.update_objects()

        # 计算奖励
        reward += self.get_reward()

        # 游戏结束检查
        if self.gunner_lives <= 0 or self.score < -20:
            self.done = True

        return self.get_state(), reward, self.done

    # 检测子弹与障碍碰撞
    def check_bullet_enemy_collision(self):
        """
        检测子弹与障碍的碰撞
        返回列表，每个元素为(bullet,enemy)的元组，表示检测到的碰撞对
        """
        collided_pairs = []
        for bullet in self.bullets_list:
            bullet_rect = pygame.Rect(bullet[0],bullet[1],self.bullet_size_x,self.bullet_size_y)
            for enemy in self.enemy_list:
                enemy_rect = pygame.Rect(enemy[0],enemy[1],self.enemy_size_x,self.enemy_size_y)
                if bullet_rect.colliderect(enemy_rect):
                    collided_pairs.append((bullet,enemy))
        return collided_pairs


    def get_reward(self):
        """ 计算奖励 """
        reward = 0
        collided_pairs = self.check_bullet_enemy_collision()
        bullets_to_remove = []
        enemies_to_remove = set()

        for bullet,enemy in collided_pairs:
            bullets_to_remove.append(bullet)
            enemies_to_remove.add(tuple(enemy))
            reward += 10
            self.score += 10
            score_sound.play()


        # **避免 remove() 报错**
        self.bullets_list = [b for b in self.bullets_list if b not in bullets_to_remove]
        self.enemy_list = [e for e in self.enemy_list if tuple(e) not in enemies_to_remove]

        if len(self.enemy_list) > 0:
            reward += 1

        if reward == 0:
            reward -= 1

        # 若角色与障碍相撞，生命值扣1
        gunner_rect = pygame.Rect(self.gunner_x, self.gunner_y, self.gunner_size_x, self.gunner_size_y)
        enemies_collided = []
        for enemy in self.enemy_list:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], self.enemy_size_x, self.enemy_size_y)
            if gunner_rect.colliderect(enemy_rect):
                be_attacked_sound.play()
                self.gunner_lives -= 1
                enemies_collided.append(enemy)
        self.enemy_list = [e for e in self.enemy_list if e not in enemies_collided]

        return reward

    # 生成障碍函数
    def spawn_enemy(self):
        if len(self.enemy_list) >= 10:
            return
        enemy_x = random.randint(0,SCREEN_WIDTH - self.enemy_size_x)
        enemy_img = get_random_enemy_image()
        enemy_img = pygame.transform.scale(enemy_img,(self.enemy_size_x,self.enemy_size_y))
        self.enemy_list.append([enemy_x,0,enemy_img])

    def update_objects(self):
        new_bullets = []
        for b in self.bullets_list:
            new_y = b[1] - self.bullet_velocity
            if new_y > 0:
                new_bullets.append([b[0], new_y])
            else:
                self.score -= 5
        self.bullets_list = new_bullets

        """ 更新子弹 & 敌人 """
        self.enemy_list = [[e[0], e[1] + self.enemy_speed, e[2]] for e in self.enemy_list if e[1] < SCREEN_HEIGHT]

        # 生成新敌人 (降低频率)
        if random.random() < 0.05:
            self.spawn_enemy()

    def render(self, screen):
        screen.blit(self.gunner_model, (self.gunner_x, self.gunner_y))

        for bullet in self.bullets_list:
            screen.blit(self.bullet_model, (bullet[0], bullet[1]))

        for enemy in self.enemy_list:
            screen.blit(enemy[2], (enemy[0], enemy[1]))
