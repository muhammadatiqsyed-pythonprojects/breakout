import asyncio

import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class Paddle:
    def __init__(self, paddle_width, paddle_height, paddle_speed):
        self.rect = pygame.FRect(0, 0, paddle_width, paddle_height)
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
        self.paddle_speed = paddle_speed

    def update(self, dt, surface):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed * dt
        self.rect.clamp_ip(surface.get_rect())

    def draw(self, surface, paddle_color):
        pygame.draw.rect(surface, paddle_color, self.rect)


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
    paddle_color = "darkblue"
    paddle_speed = 500  # pixels per second
    paddle_width = 100
    paddle_height = 20
    paddle = Paddle(paddle_width, paddle_height, paddle_speed)

    # game loop
    while running:
        # -------------------------------INPUT---------------------------------------
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ----------------------------------UPDATE-------------------------------------

        paddle.update(dt, window)

        # ---------------------------------DRAW---------------------------------------
        window.fill("white")

        paddle.draw(window, paddle_color)

        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


asyncio.run(main())
