import pygame.display


# 定义全局颜色
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# 游戏窗口设置
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))



# 渲染游戏结束
def game_over_screen(screen,font, score):
    # 游戏结束
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    screen.fill(WHITE)
    game_over_text = font.render("GAME OVER", True, BLACK)
    final_score_text = font.render(f"Final Score: {score}", True, BLACK)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10))

    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()


# 渲染左上角分数、生命值显示
def draw_ui(screen,font, score, gunner_lives):
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, 70))
    score_text = font.render(f"Score: {score}", True, BLACK)
    lives_text = font.render(f"Lives: {gunner_lives}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
