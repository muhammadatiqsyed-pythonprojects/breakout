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
BALL_SPEED = 300  # pixels per second, in any direction


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
    def __init__(self, ball_color, ball_radius, ball_speed):
        self.rect = pygame.FRect(0, 0, ball_radius * 2, ball_radius * 2)
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        # direction up and to the right, length 1, then multiplied by the speed
        self.velocity = pygame.Vector2(1, -1).normalize() * ball_speed
        self.speed = ball_speed
        self.ball_color = ball_color
        self.ball_radius = ball_radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.ball_color, self.rect.center, self.ball_radius)

    def update(self, dt, paddle_rect):
        # move
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        # walls
        if self.rect.left <= 0:
            self.rect.left = 0
            self.velocity.x = abs(self.velocity.x)
        if self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.velocity.x = -abs(self.velocity.x)
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity.y = abs(self.velocity.y)
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity.y = -abs(self.velocity.y)

        # paddle
        if (
            self.rect.colliderect(paddle_rect)
            and self.velocity.y > 0
            and self.rect.centery < paddle_rect.centery
        ):
            self.rect.bottom = paddle_rect.top
            # where did the ball hit? -1 = far left, 0 = centre, 1 = far right
            offset = (self.rect.centerx - paddle_rect.centerx) / (paddle_rect.width / 2)
            offset = max(-1, min(1, offset))
            # new direction: sideways by the offset, always upward
            direction = pygame.Vector2(offset * 0.8, -1)
            self.velocity = direction.normalize() * self.speed


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
    ball = Ball(BALL_COLOR, BALL_RADIUS, BALL_SPEED)

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
