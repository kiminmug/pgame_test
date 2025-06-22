import pygame
import sys
import random

# 게임 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 102, 204)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# 난이도 설정
DIFFICULTY_SETTINGS = {
    'easy':   {'paddle_width': 140, 'ball_speed': 4, 'brick_rows': 4},
    'normal': {'paddle_width': 100, 'ball_speed': 5, 'brick_rows': 6},
    'hard':   {'paddle_width': 70,  'ball_speed': 7, 'brick_rows': 8},
}

PADDLE_HEIGHT = 15
PADDLE_SPEED = 8
BALL_RADIUS = 10
BRICK_COLS = 10
BRICK_WIDTH = 70
BRICK_HEIGHT = 25
BRICK_PADDING = 10
BRICK_OFFSET_TOP = 50
BRICK_OFFSET_LEFT = 35

class Paddle:
    def __init__(self, width):
        self.rect = pygame.Rect((SCREEN_WIDTH - width) // 2, SCREEN_HEIGHT - 40, width, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED
        self.width = width

    def move(self, direction):
        if direction == 'left':
            self.rect.x -= self.speed
        elif direction == 'right':
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.width))

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

class Ball:
    def __init__(self, speed):
        self.init_speed = speed
        self.reset()

    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.radius = BALL_RADIUS
        self.dx = random.choice([-1, 1]) * self.init_speed
        self.dy = -self.init_speed

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # 벽 충돌
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.dx *= -1
            return 'wall'
        if self.y - self.radius <= 0:
            self.dy *= -1
            return 'wall'
        return None

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Brick:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.alive = True

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)

def create_bricks(rows):
    bricks = []
    colors = [YELLOW, GREEN, BLUE, RED, (255, 128, 0), (128, 0, 255)]
    for row in range(rows):
        for col in range(BRICK_COLS):
            x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
            y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
            color = colors[row % len(colors)]
            bricks.append(Brick(x, y, color))
    return bricks

def draw_text(screen, text, size, x, y, color=WHITE):
    # 한글 폰트 사용 (맑은 고딕, 시스템에 없으면 기본 폰트)
    try:
        font = pygame.font.SysFont('malgungothic', size, bold=True)
    except:
        font = pygame.font.SysFont('arial', size, bold=True)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    rect.center = (x, y)
    screen.blit(surface, rect)

def select_difficulty(screen):
    selecting = True
    clock = pygame.time.Clock()
    while selecting:
        screen.fill(BLACK)
        draw_text(screen, '난이도 선택', 60, SCREEN_WIDTH // 2, 120, YELLOW)
        draw_text(screen, '1: 초보 (쉬움)', 40, SCREEN_WIDTH // 2, 220, WHITE)
        draw_text(screen, '2: 중급 (보통)', 40, SCREEN_WIDTH // 2, 300, WHITE)
        draw_text(screen, '3: 고급 (어려움)', 40, SCREEN_WIDTH // 2, 380, WHITE)
        draw_text(screen, '숫자키(1~3)를 눌러 선택하세요', 30, SCREEN_WIDTH // 2, 480, GREEN)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'easy'
                elif event.key == pygame.K_2:
                    return 'normal'
                elif event.key == pygame.K_3:
                    return 'hard'
        clock.tick(30)

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('아카노이드')
    clock = pygame.time.Clock()

    # 사운드 로드
    try:
        ping_sound = pygame.mixer.Sound('ping.wav')
    except Exception:
        ping_sound = None

    # 난이도 선택
    difficulty = select_difficulty(screen)
    settings = DIFFICULTY_SETTINGS[difficulty]
    paddle = Paddle(settings['paddle_width'])
    ball = Ball(settings['ball_speed'])
    bricks = create_bricks(settings['brick_rows'])
    score = 0
    running = True
    game_over = False
    win = False

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move('left')
        if keys[pygame.K_RIGHT]:
            paddle.move('right')

        if not game_over:
            collision = ball.move()
            if collision == 'wall' and ping_sound:
                ping_sound.play()

            # 패들 충돌
            if ball.rect().colliderect(paddle.rect):
                ball.dy *= -1
                ball.y = paddle.rect.y - ball.radius
                if ping_sound:
                    ping_sound.play()

            # 벽돌 충돌
            for brick in bricks:
                if brick.alive and ball.rect().colliderect(brick.rect):
                    brick.alive = False
                    score += 10
                    # 충돌 방향 반전
                    if abs(ball.x - brick.rect.left) < ball.radius or abs(ball.x - brick.rect.right) < ball.radius:
                        ball.dx *= -1
                    else:
                        ball.dy *= -1
                    if ping_sound:
                        ping_sound.play()
                    break

            # 바닥에 떨어짐
            if ball.y - ball.radius > SCREEN_HEIGHT:
                game_over = True
                win = False

            # 모든 벽돌 제거
            if all(not brick.alive for brick in bricks):
                game_over = True
                win = True

        # 그리기
        screen.fill(BLACK)
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)
        draw_text(screen, f'점수: {score}', 30, 80, 20)

        if game_over:
            if win:
                draw_text(screen, '축하합니다! 클리어!', 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, YELLOW)
            else:
                draw_text(screen, '게임 오버', 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, RED)
            draw_text(screen, 'R: 다시 시작   Q: 종료', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # 난이도 재선택
                difficulty = select_difficulty(screen)
                settings = DIFFICULTY_SETTINGS[difficulty]
                paddle = Paddle(settings['paddle_width'])
                ball = Ball(settings['ball_speed'])
                bricks = create_bricks(settings['brick_rows'])
                score = 0
                game_over = False
                win = False
            if keys[pygame.K_q]:
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main() 