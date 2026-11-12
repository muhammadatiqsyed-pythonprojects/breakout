import asyncio

import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


async def main():
    # ---------------------------------------SET UP---------------------------------------
    pygame.init()
    window = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED | pygame.RESIZABLE
    )
    pygame.display.set_caption("breakout")
    clock = pygame.time.Clock()

    # variables
    running = True

    # game loop
    while running:
        # -------------------------------INPUT---------------------------------------
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ---------------------------------DRAW---------------------------------------
        window.fill("white")

        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


asyncio.run(main())
