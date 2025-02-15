import numpy as np
import pygame
import random

# 游戏窗口大小
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 700

class ApocalypseGunnerEnv:
    def __init__(self, is_training=False):
        """ 初始化游戏环境
        :param is_training: 是否用于 AI 训练模式 (AI 训练不需要 Pygame 渲染)
        """
        self.gunner_size_x, self.gunner_size_y = 50, 50
        self.bullet_size_x, self.bullet_size_y = 5, 10
        self.enemy_size_x, self.enemy_size_y = 50, 50
        self.gunner_speed = 5
        self.bullet_velocity = 7
        self.enemy_speed = 3
        self.is_training = is_training  # AI 训练模式不渲染画面

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
        enemies = np.array([(enemy[0] / SCREEN_WIDTH, enemy[1] / SCREEN_HEIGHT) for enemy in self.enemy_list]).flatten()
        bullets = np.array(
            [(bullet[0] / SCREEN_WIDTH, bullet[1] / SCREEN_HEIGHT) for bullet in self.bullets_list]).flatten()

        if len(enemies) == 0:
            enemies = np.zeros(2)
        if len(bullets) == 0:
            bullets = np.zeros(2)

        return np.concatenate(([self.gunner_x / SCREEN_WIDTH, self.gunner_y / SCREEN_HEIGHT], enemies, bullets))

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
            self.bullets_list.append([self.gunner_x + self.gunner_size_x // 2, self.gunner_y])

        # **即使无输入，也要更新游戏状态**
        self.update_objects()

        # 计算奖励
        reward += self.get_reward()

        # 游戏结束检查
        if self.gunner_lives <= 0:
            self.done = True

        return self.get_state(), reward, self.done

    def get_reward(self):
        """ 计算奖励 """
        reward = 0
        bullets_to_remove = []
        enemies_to_remove = set()

        for bullet in self.bullets_list:
            for enemy in self.enemy_list:
                if (bullet[0] < enemy[0] + self.enemy_size_x and bullet[0] > enemy[0]
                        and bullet[1] < enemy[1] + self.enemy_size_y and bullet[1] > enemy[1]):
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.add(tuple(enemy))
                    reward += 10

        # **避免 remove() 报错**
        self.bullets_list = [b for b in self.bullets_list if b not in bullets_to_remove]
        self.enemy_list = [e for e in self.enemy_list if tuple(e) not in enemies_to_remove]

        if len(self.enemy_list) > 0:
            reward += 1

        if reward == 0:
            reward -= 1

        return reward

    def update_objects(self):
        """ 更新子弹 & 敌人 """
        self.bullets_list = [[b[0], b[1] - self.bullet_velocity] for b in self.bullets_list if b[1] > 0]
        self.enemy_list = [[e[0], e[1] + self.enemy_speed] for e in self.enemy_list if e[1] < SCREEN_HEIGHT]

        # 生成新敌人 (降低频率)
        if random.random() < 0.05:
            enemy_x = random.randint(0, SCREEN_WIDTH - self.enemy_size_x)
            self.enemy_list.append([enemy_x, 0])

    def render(self, screen):
        """ 仅在非 AI 训练模式下渲染游戏 """
        if self.is_training:
            return

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (0, 0, 255), (self.gunner_x, self.gunner_y, self.gunner_size_x, self.gunner_size_y))

        for bullet in self.bullets_list:
            pygame.draw.rect(screen, (255, 0, 0), (bullet[0], bullet[1], 5, 10))

        for enemy in self.enemy_list:
            pygame.draw.rect(screen, (0, 0, 0), (enemy[0], enemy[1], self.gunner_size_x, self.gunner_size_y))

        pygame.display.update()
