import asyncio

import pygame

# main surface dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# paddle values
PADDLE_COLOR = "darkblue"
PADDLE_SPEED = 500  # pixels per second
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20

# ball values
BALL_COLOR = "pink"
BALL_RADIUS = 12
BALL_SPEED_X = 200  # pixels per second
BALL_SPEED_Y = 200


class Paddle:
    def __init__(self, paddle_width, paddle_height, paddle_speed):
        self.rect = pygame.FRect(0, 0, paddle_width, paddle_height)
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
        self.paddle_speed = paddle_speed

    def update(self, dt, surface):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.paddle_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.paddle_speed * dt
        self.rect.clamp_ip(surface.get_rect())

    def draw(self, surface, paddle_color):
        pygame.draw.rect(surface, paddle_color, self.rect)


class Ball:
    def __init__(self, ball_color, ball_radius, ball_speed_x, ball_speed_y):
        self.rect = pygame.FRect(0, 0, ball_radius * 2, ball_radius * 2)
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.ball_speed_x = ball_speed_x
        self.ball_speed_y = ball_speed_y
        self.ball_color = ball_color
        self.ball_radius = ball_radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.ball_color, self.rect.center, self.ball_radius)

    def update(self, dt, paddle_rect):
        self.rect.x += self.ball_speed_x * dt
        self.rect.y += self.ball_speed_y * dt
        if self.rect.left <= 0:
            self.rect.left = 0
            self.ball_speed_x = abs(self.ball_speed_x)
        if self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.ball_speed_x = -abs(self.ball_speed_x)
        if self.rect.top <= 0:
            self.rect.top = 0
            self.ball_speed_y = abs(self.ball_speed_y)
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.ball_speed_y = -abs(self.ball_speed_y)
        if self.rect.colliderect(paddle_rect) and self.ball_speed_y > 0:
            self.rect.bottom = paddle_rect.top
            self.ball_speed_y = -abs(self.ball_speed_y)


async def main():
    # ---------------------------------------SET UP---------------------------------------
    pygame.init()
    # main surface
    window = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED | pygame.RESIZABLE
    )
    pygame.display.set_caption("breakout")
    clock = pygame.time.Clock()

    # variables
    running = True

    # paddle class object
    paddle = Paddle(PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED)

    # ball class object
    ball = Ball(BALL_COLOR, BALL_RADIUS, BALL_SPEED_X, BALL_SPEED_Y)

    # game loop
    while running:
        # -------------------------------INPUT---------------------------------------
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ----------------------------------UPDATE-------------------------------------

        paddle.update(dt, window)

        ball.update(dt, paddle.rect)

        # ---------------------------------DRAW---------------------------------------
        window.fill("white")

        paddle.draw(window, PADDLE_COLOR)

        ball.draw(window)

        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


asyncio.run(main())
