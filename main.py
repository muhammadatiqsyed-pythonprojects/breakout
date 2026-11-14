import asyncio
import os

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
BALL_COLOR = "red"
BALL_RADIUS = 12
BALL_SPEED = 300  # starting speed, pixels per second
BALL_MAX_SPEED = 450  # the ball never gets faster than this
BALL_SPEEDUP = 10  # speed added on every paddle hit
BALL_START_POS = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150)

# brick values (use your own values here if you changed them earlier)
BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_WIDTH = 50
BRICK_HEIGHT = 30
BRICK_GAP = 5
BRICK_TOP_MARGIN = 60
BRICK_LEFT_MARGIN = (
    WINDOW_WIDTH - (BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_GAP)
) / 2
# one colour per row (repeats if there are more rows than colours)
BRICK_COLORS = ["darkorange", "gold", "forestgreen", "teal", "purple", "brown"]

# game values
STARTING_LIVES = 3
POINTS_PER_BRICK = 5  # bottom row; each row higher is worth this much more
LIFE_LOST_PAUSE = 2  # seconds the game waits after losing a life

# assets (every file is optional: if one is missing, a shape or silence is used)
ASSET_DIR = "assets"
SOUND_VOLUME = 0.5
SOUND_FILES = {
    "bounce": "bounce.ogg",  # ball hits a wall or the paddle
    "brick": "brick.ogg",  # ball breaks a brick
    "life_lost": "life_lost.ogg",
    "game_over": "game_over.ogg",
    "win": "win.ogg",
}
BACKGROUND_FILE = "background.png"
PADDLE_FILE = "paddle.png"
BALL_FILE = "ball.png"

# text
TEXT_COLOR = "black"
CONTROLS_TEXT = [
    "Left / Right or A / D : move paddle",
    "P : pause",
    "R : restart (paused or game over)",
    "Space or Enter : start",
]


class Paddle:
    def __init__(self, paddle_width, paddle_height, paddle_speed):
        self.rect = pygame.FRect(0, 0, paddle_width, paddle_height)
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
        self.paddle_speed = paddle_speed

    def reset(self):
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)

    def update(self, dt, surface):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.paddle_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.paddle_speed * dt
        self.rect.clamp_ip(surface.get_rect())

    def draw(self, surface, paddle_color, image=None):
        if image:
            surface.blit(image, (int(self.rect.x), int(self.rect.y)))
        else:
            pygame.draw.rect(surface, paddle_color, self.rect)


class Ball:
    def __init__(self, ball_color, ball_radius, ball_speed):
        self.rect = pygame.FRect(0, 0, ball_radius * 2, ball_radius * 2)
        self.base_speed = ball_speed
        self.ball_color = ball_color
        self.ball_radius = ball_radius
        self.reset()

    def reset(self):
        # back to the start position, start speed and start direction
        self.rect.center = BALL_START_POS
        self.speed = self.base_speed
        self.velocity = pygame.Vector2(1, -1).normalize() * self.speed

    def draw(self, surface, image=None):
        if image:
            surface.blit(image, image.get_rect(center=self.rect.center))
        else:
            pygame.draw.circle(
                surface, self.ball_color, self.rect.center, self.ball_radius
            )

    def update(self, dt, paddle_rect):
        # returns "bounce" if the ball hit a wall or the paddle, otherwise None
        hit = None

        # move
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        # walls (there is no bottom wall: the ball can fall out)
        if self.rect.left <= 0:
            self.rect.left = 0
            self.velocity.x = abs(self.velocity.x)
            hit = "bounce"
        if self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.velocity.x = -abs(self.velocity.x)
            hit = "bounce"
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity.y = abs(self.velocity.y)
            hit = "bounce"

        # paddle
        if (
            self.rect.colliderect(paddle_rect)
            and self.velocity.y > 0
            and self.rect.centery < paddle_rect.centery
        ):
            self.rect.bottom = paddle_rect.top
            # speed up a little, but never past the maximum
            self.speed = min(self.speed + BALL_SPEEDUP, BALL_MAX_SPEED)
            # where did the ball hit? -1 = far left, 0 = centre, 1 = far right
            offset = (self.rect.centerx - paddle_rect.centerx) / (paddle_rect.width / 2)
            offset = max(-1, min(1, offset))
            # new direction: sideways by the offset, always upward
            direction = pygame.Vector2(offset * 0.8, -1)
            self.velocity = direction.normalize() * self.speed
            hit = "bounce"

        return hit

    def bounce_off(self, brick_rect):
        # how deep the ball has sunk into the brick from each side
        overlap_left = self.rect.right - brick_rect.left
        overlap_right = brick_rect.right - self.rect.left
        overlap_top = self.rect.bottom - brick_rect.top
        overlap_bottom = brick_rect.bottom - self.rect.top

        # the smallest overlap is the side the ball came in through
        smallest = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if smallest == overlap_left:
            self.rect.right = brick_rect.left
            self.velocity.x = -abs(self.velocity.x)
        elif smallest == overlap_right:
            self.rect.left = brick_rect.right
            self.velocity.x = abs(self.velocity.x)
        elif smallest == overlap_top:
            self.rect.bottom = brick_rect.top
            self.velocity.y = -abs(self.velocity.y)
        else:
            self.rect.top = brick_rect.bottom
            self.velocity.y = abs(self.velocity.y)


class Brick:
    def __init__(self, x, y, brick_color, brick_width, brick_height, points):
        self.rect = pygame.FRect(x, y, brick_width, brick_height)
        self.brick_color = brick_color
        self.points = points

    def draw(self, surface):
        pygame.draw.rect(surface, self.brick_color, self.rect)


class Button:
    def __init__(self, center, size, label, color):
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = center
        self.label = label
        self.color = color

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        text = font.render(self.label, True, "white")
        surface.blit(text, text.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def build_bricks():
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = BRICK_LEFT_MARGIN + col * (BRICK_WIDTH + BRICK_GAP)
            y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_GAP)
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            points = POINTS_PER_BRICK * (BRICK_ROWS - row)  # top rows pay more
            bricks.append(Brick(x, y, color, BRICK_WIDTH, BRICK_HEIGHT, points))
    return bricks


def load_sound(filename):
    # returns a Sound, or None if the file is missing or audio is unavailable
    try:
        sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "sounds", filename))
        sound.set_volume(SOUND_VOLUME)
        return sound
    except (FileNotFoundError, pygame.error):
        return None


def play(sound):
    if sound:
        sound.play()


def load_image(filename, size):
    # returns a scaled image, or None if the file is missing
    try:
        image = pygame.image.load(os.path.join(ASSET_DIR, "images", filename))
        return pygame.transform.smoothscale(image.convert_alpha(), size)
    except (FileNotFoundError, pygame.error):
        return None


def draw_text(surface, text, font, color, **position):
    # position is like center=(400, 100) or topleft=(10, 10)
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(**position))


async def main():
    # ---------------------------------------SET UP---------------------------------------
    pygame.init()
    # main surface
    window = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED | pygame.RESIZABLE
    )
    pygame.display.set_caption("breakout")
    clock = pygame.time.Clock()

    # fonts (created once, not every frame)
    title_font = pygame.font.Font(None, 90)
    text_font = pygame.font.Font(None, 44)
    small_font = pygame.font.Font(None, 30)

    # sounds and images (None means "not found": shapes and silence are used)
    sounds = {name: load_sound(file) for name, file in SOUND_FILES.items()}
    background_image = load_image(BACKGROUND_FILE, (WINDOW_WIDTH, WINDOW_HEIGHT))
    paddle_image = load_image(PADDLE_FILE, (PADDLE_WIDTH, PADDLE_HEIGHT))
    ball_image = load_image(BALL_FILE, (BALL_RADIUS * 2, BALL_RADIUS * 2))

    # variables
    running = True
    game_state = "menu"  # menu, playing, paused, gameover, win
    score = 0
    lives = STARTING_LIVES
    high_score = 0
    new_high = False
    life_lost_timer = 0

    # objects
    paddle = Paddle(PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED)
    ball = Ball(BALL_COLOR, BALL_RADIUS, BALL_SPEED)
    brick_list = build_bricks()
    start_button = Button((WINDOW_WIDTH // 2, 480), (220, 60), "Start", "darkblue")
    restart_button = Button((WINDOW_WIDTH // 2, 430), (220, 60), "Restart", "darkblue")

    # game loop
    while running:
        # -------------------------------INPUT---------------------------------------
        # dt is capped so the ball cannot jump after the window is dragged
        dt = min(clock.tick(60) / 1000, 0.05)
        restart = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "menu":
                if start_button.is_clicked(event):
                    restart = True
                if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                ):
                    restart = True

            elif game_state == "playing":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    game_state = "paused"

            elif game_state == "paused":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game_state = "playing"
                    elif event.key == pygame.K_r:
                        restart = True

            elif game_state in ("gameover", "win"):
                if restart_button.is_clicked(event):
                    restart = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    restart = True

        # starting and restarting share the same code
        if restart:
            score = 0
            lives = STARTING_LIVES
            new_high = False
            brick_list = build_bricks()
            ball.reset()
            paddle.reset()
            game_state = "playing"

        # ----------------------------------UPDATE-------------------------------------
        if game_state == "playing":
            paddle.update(dt, window)
            if ball.update(dt, paddle.rect) == "bounce":
                play(sounds["bounce"])

            # bounce off and remove the first brick the ball touches
            for brick in brick_list[:]:  # [:] loops over a copy of the list
                if brick.rect.colliderect(ball.rect):
                    ball.bounce_off(brick.rect)
                    brick_list.remove(brick)
                    score += brick.points
                    play(sounds["brick"])
                    break

            # ball fell below the window: lose a life and reset the ball
            if ball.rect.top > WINDOW_HEIGHT:
                lives -= 1
                ball.reset()
                if lives > 0:
                    game_state = "life_lost"
                    life_lost_timer = LIFE_LOST_PAUSE
                    play(sounds["life_lost"])

            # end of the game
            if lives <= 0 or not brick_list:
                game_state = "gameover" if lives <= 0 else "win"
                play(sounds["game_over"] if lives <= 0 else sounds["win"])
                new_high = score > high_score
                if new_high:
                    high_score = score

        elif game_state == "life_lost":
            life_lost_timer -= dt
            if life_lost_timer <= 0:
                game_state = "playing"

        # ---------------------------------DRAW---------------------------------------
        if background_image:
            window.blit(background_image, (0, 0))
        else:
            window.fill("white")
        centre_x = WINDOW_WIDTH // 2

        if game_state == "menu":
            draw_text(
                window, "BREAKOUT", title_font, "darkblue", center=(centre_x, 110)
            )
            for i, line in enumerate(CONTROLS_TEXT):
                draw_text(
                    window,
                    line,
                    text_font,
                    TEXT_COLOR,
                    center=(centre_x, 220 + i * 45),
                )
            start_button.draw(window, text_font)

        elif game_state in ("playing", "paused", "life_lost"):
            for brick in brick_list:
                brick.draw(window)
            paddle.draw(window, PADDLE_COLOR, paddle_image)
            ball.draw(window, ball_image)

            # HUD
            draw_text(
                window, f"Score: {score}", small_font, TEXT_COLOR, topleft=(10, 10)
            )
            draw_text(
                window,
                f"Lives: {lives}",
                small_font,
                TEXT_COLOR,
                topright=(WINDOW_WIDTH - 10, 10),
            )
            draw_text(window, "P: pause", small_font, "gray30", midtop=(centre_x, 10))

            if game_state == "paused":
                draw_text(
                    window, "PAUSED", title_font, "darkblue", center=(centre_x, 340)
                )
                draw_text(
                    window,
                    "P: resume    R: restart",
                    text_font,
                    TEXT_COLOR,
                    center=(centre_x, 400),
                )

            if game_state == "life_lost":
                if lives == 1:
                    message = "Only 1 life remaining!"
                else:
                    message = f"{lives} lives remaining"
                draw_text(window, message, text_font, "red", center=(centre_x, 340))
                draw_text(
                    window,
                    f"Get ready... {int(life_lost_timer) + 1}",
                    small_font,
                    TEXT_COLOR,
                    center=(centre_x, 385),
                )

        elif game_state in ("gameover", "win"):
            title = "GAME OVER" if game_state == "gameover" else "YOU WIN!"
            draw_text(window, title, title_font, "darkblue", center=(centre_x, 130))
            draw_text(
                window, f"Score: {score}", text_font, TEXT_COLOR, center=(centre_x, 230)
            )
            draw_text(
                window,
                f"High score: {high_score}",
                text_font,
                TEXT_COLOR,
                center=(centre_x, 280),
            )
            if new_high:
                draw_text(
                    window,
                    "New high score!",
                    text_font,
                    "forestgreen",
                    center=(centre_x, 335),
                )
            restart_button.draw(window, text_font)
            draw_text(
                window, "or press R", small_font, "gray30", center=(centre_x, 490)
            )

        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


asyncio.run(main())
