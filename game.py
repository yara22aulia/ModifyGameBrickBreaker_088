
import pygame
import random
import math
import json
from pathlib import Path

# ==========================================
# NEON BRICK BREAKER - HEXAGON EDITION
# ==========================================

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Brick Breaker - Hexagon Edition")

CLOCK = pygame.time.Clock()

# Warna
BG = (12, 15, 35)
WHITE = (240, 245, 255)
CYAN = (40, 220, 255)
PINK = (255, 75, 160)
PURPLE = (155, 100, 255)
YELLOW = (255, 220, 70)
GREEN = (70, 240, 160)
RED = (255, 85, 95)
MUTED = (145, 160, 190)

# Font
FONT_SMALL = pygame.font.SysFont("arial", 18)
FONT_MEDIUM = pygame.font.SysFont("arial", 25, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 48, bold=True)

HIGH_SCORE_FILE = Path("brick_breaker_highscore.json")


# ==========================================
# SISTEM HIGH SCORE
# ==========================================

def load_high_score():
    try:
        if HIGH_SCORE_FILE.exists():
            data = json.loads(
                HIGH_SCORE_FILE.read_text(encoding="utf-8")
            )
            return int(data.get("high_score", 0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass

    return 0


def save_high_score(value):
    try:
        HIGH_SCORE_FILE.write_text(
            json.dumps({"high_score": int(value)}),
            encoding="utf-8"
        )
    except OSError:
        pass


# ==========================================
# CLASS PADDLE
# ==========================================

class Paddle:

    def __init__(self):
        self.width = 115
        self.height = 15

        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 55

        self.speed = 8

        self.rect = pygame.Rect(
            self.x, self.y,
            self.width, self.height
        )

        self.wide_timer = 0

    def update(self, keys):

        direction = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1

        self.x += direction * self.speed

        self.x = max(
            0,
            min(WIDTH - self.width, self.x)
        )

        self.rect.x = round(self.x)

        if self.wide_timer > 0:

            self.wide_timer -= 1

            if self.wide_timer == 0:
                self.width = 115
                self.rect.width = self.width

                self.x = min(
                    self.x,
                    WIDTH - self.width
                )

                self.rect.x = round(self.x)

    def make_wide(self):

        self.width = 175
        self.rect.width = self.width

        self.wide_timer = FPS * 8

        self.x = min(
            self.x,
            WIDTH - self.width
        )

        self.rect.x = round(self.x)

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            CYAN,
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            surface,
            WHITE,
            self.rect,
            2,
            border_radius=8
        )

        pygame.draw.line(
            surface,
            WHITE,
            (self.rect.left + 18, self.rect.centery),
            (self.rect.right - 18, self.rect.centery),
            2
        )


# ==========================================
# CLASS BALL
# ==========================================

class Ball:

    def __init__(self, paddle):

        self.radius = 9
        self.speed = 5.2

        self.x = paddle.rect.centerx
        self.y = paddle.rect.top - self.radius - 2

        self.dx = 0
        self.dy = 0

        self.rect = pygame.Rect(
            0, 0,
            self.radius * 2,
            self.radius * 2
        )

        self.update_rect()

    def update_rect(self):

        self.rect.center = (
            round(self.x),
            round(self.y)
        )

    def attach_to_paddle(self, paddle):

        self.x = paddle.rect.centerx
        self.y = paddle.rect.top - self.radius - 2

        self.dx = 0
        self.dy = 0

        self.update_rect()

    def launch(self):

        if self.dx == 0 and self.dy == 0:

            self.dx = random.choice(
                [-0.65, 0.65]
            ) * self.speed

            self.dy = -math.sqrt(
                self.speed ** 2 - self.dx ** 2
            )

    def update(self):

        if self.dx == 0 and self.dy == 0:
            return False

        self.x += self.dx
        self.y += self.dy

        self.update_rect()

        # Pantulan dinding kiri
        if self.rect.left <= 0:

            self.rect.left = 0
            self.x = self.rect.centerx
            self.dx = abs(self.dx)

        # Pantulan dinding kanan
        elif self.rect.right >= WIDTH:

            self.rect.right = WIDTH
            self.x = self.rect.centerx
            self.dx = -abs(self.dx)

        # Pantulan dinding atas
        if self.rect.top <= 65:

            self.rect.top = 65
            self.y = self.rect.centery
            self.dy = abs(self.dy)

        # Bola jatuh
        return self.rect.top > HEIGHT

    def bounce_from_paddle(self, paddle):

        offset = (
            self.rect.centerx - paddle.rect.centerx
        ) / (paddle.width / 2)

        offset = max(-0.9, min(0.9, offset))

        self.dx = offset * self.speed

        self.dy = -math.sqrt(
            max(1, self.speed ** 2 - self.dx ** 2)
        )

        self.rect.bottom = paddle.rect.top
        self.y = self.rect.centery

    def draw(self, surface):

        pygame.draw.circle(
            surface,
            WHITE,
            (round(self.x), round(self.y)),
            self.radius
        )

        pygame.draw.circle(
            surface,
            CYAN,
            (round(self.x), round(self.y)),
            self.radius,
            2
        )


# ==========================================
# CLASS BRICK - HEXAGON
# ==========================================

class Brick:

    def __init__(self, x, y, width, height, strength):

        self.rect = pygame.Rect(
            x, y, width, height
        )

        self.max_health = strength
        self.health = strength

        self.colors = {
            1: PINK,
            2: PURPLE,
            3: YELLOW
        }

    def hit(self):

        self.health -= 1

        return self.health <= 0

    def draw(self, surface):

        color = self.colors[self.health]

        # Ukuran balok
        x = self.rect.x
        y = self.rect.y
        w = self.rect.width
        h = self.rect.height

        # Membuat bentuk segi enam
        points = [
            (x + w * 0.25, y),
            (x + w * 0.75, y),
            (x + w, y + h * 0.5),
            (x + w * 0.75, y + h),
            (x + w * 0.25, y + h),
            (x, y + h * 0.5)
        ]

        # Bayangan balok
        shadow_points = [
            (int(px + 3), int(py + 4))
            for px, py in points
        ]

        pygame.draw.polygon(
            surface,
            (5, 5, 20),
            shadow_points
        )

        # Badan utama balok
        pygame.draw.polygon(
            surface,
            color,
            points
        )

        # Garis tepi putih
        pygame.draw.polygon(
            surface,
            WHITE,
            points,
            2
        )

        # Menampilkan ketahanan balok
        if self.max_health > 1:

            label = FONT_SMALL.render(
                str(self.health),
                True,
                BG
            )

            surface.blit(
                label,
                label.get_rect(center=self.rect.center)
            )


# ==========================================
# CLASS POWER UP
# ==========================================

class PowerUp:

    def __init__(self, x, y):

        self.rect = pygame.Rect(
            x - 10,
            y - 10,
            20,
            20
        )

        self.speed = 3
        self.color = GREEN

    def update(self):

        self.rect.y += self.speed

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            self.color,
            self.rect,
            border_radius=5
        )

        pygame.draw.rect(
            surface,
            WHITE,
            self.rect,
            2,
            border_radius=5
        )

        label = FONT_SMALL.render(
            "W",
            True,
            BG
        )

        surface.blit(
            label,
            label.get_rect(center=self.rect.center)
        )


# ==========================================
# MEMBUAT BALOK
# ==========================================

def create_bricks(level):

    bricks = []

    columns = 10
    rows = min(4 + level, 7)

    gap = 7
    margin = 35

    brick_width = (
        WIDTH - 2 * margin - (columns - 1) * gap
    ) // columns

    brick_height = 23

    for row in range(rows):

        for col in range(columns):

            x = margin + col * (
                brick_width + gap
            )

            y = 90 + row * (
                brick_height + gap
            )

            strength = min(
                3,
                1 + (row + level - 1) // 3
            )

            bricks.append(
                Brick(
                    x,
                    y,
                    brick_width,
                    brick_height,
                    strength
                )
            )

    return bricks


# ==========================================
# FUNGSI MENAMPILKAN TEKS
# ==========================================

def draw_text(
    surface,
    text,
    font,
    color,
    x,
    y,
    center=False
):

    image = font.render(
        text,
        True,
        color
    )

    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(image, rect)


# ==========================================
# RESET GAME
# ==========================================

def reset_game():

    paddle = Paddle()
    ball = Ball(paddle)

    bricks = create_bricks(1)

    powerups = []

    lives = 3
    score = 0
    level = 1

    state = "ready"

    return (
        paddle,
        ball,
        bricks,
        powerups,
        lives,
        score,
        level,
        state
    )


# ==========================================
# MAIN GAME
# ==========================================

def main():

    high_score = load_high_score()

    (
        paddle,
        ball,
        bricks,
        powerups,
        lives,
        score,
        level,
        state
    ) = reset_game()

    running = True

    while running:

        CLOCK.tick(FPS)

        # EVENT HANDLING
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    running = False

                elif event.key == pygame.K_SPACE:

                    if state == "ready":

                        ball.launch()
                        state = "playing"

                    elif state in ("won", "lost"):

                        (
                            paddle,
                            ball,
                            bricks,
                            powerups,
                            lives,
                            score,
                            level,
                            state
                        ) = reset_game()

                elif event.key == pygame.K_p:

                    if state == "playing":
                        state = "paused"

                    elif state == "paused":
                        state = "playing"

                elif event.key == pygame.K_r:

                    (
                        paddle,
                        ball,
                        bricks,
                        powerups,
                        lives,
                        score,
                        level,
                        state
                    ) = reset_game()

        keys = pygame.key.get_pressed()

        # ==================================
        # UPDATE GAME
        # ==================================

        if state == "playing":

            paddle.update(keys)

            # Update bola
            if ball.update():

                lives -= 1

                if lives <= 0:

                    state = "lost"

                else:

                    ball.attach_to_paddle(paddle)
                    state = "ready"

            # Tabrakan bola dan paddle
            if (
                ball.dy > 0
                and ball.rect.colliderect(paddle.rect)
            ):

                ball.bounce_from_paddle(paddle)

            # Tabrakan bola dan brick
            for brick in bricks[:]:

                if ball.rect.colliderect(brick.rect):

                    previous = ball.rect.move(
                        -round(ball.dx),
                        -round(ball.dy)
                    )

                    if (
                        previous.bottom <= brick.rect.top
                        or previous.top >= brick.rect.bottom
                    ):

                        ball.dy *= -1

                    else:

                        ball.dx *= -1

                    destroyed = brick.hit()

                    if destroyed:

                        bricks.remove(brick)

                        score += 10 * brick.max_health

                        # Kesempatan mendapatkan power-up
                        if random.random() < 0.16:

                            powerups.append(
                                PowerUp(
                                    brick.rect.centerx,
                                    brick.rect.centery
                                )
                            )

                    else:

                        score += 2

                    break

            # Update power-up
            for item in powerups[:]:

                item.update()

                if item.rect.colliderect(paddle.rect):

                    paddle.make_wide()
                    powerups.remove(item)

                elif item.rect.top > HEIGHT:

                    powerups.remove(item)

            # Naik level jika semua balok hancur
            if not bricks:

                level += 1

                paddle = Paddle()
                ball = Ball(paddle)

                ball.speed = min(
                    8.5,
                    5.2 + (level - 1) * 0.55
                )

                bricks = create_bricks(level)

                powerups.clear()

                state = "ready"

        else:

            if state == "ready":

                paddle.update(keys)
                ball.attach_to_paddle(paddle)

        # Update high score
        if score > high_score:

            high_score = score
            save_high_score(high_score)

        # ==================================
        # DISPLAY
        # ==================================

        SCREEN.fill(BG)

        # Panel informasi
        pygame.draw.line(
            SCREEN,
            PURPLE,
            (0, 65),
            (WIDTH, 65),
            2
        )

        draw_text(
            SCREEN,
            f"SKOR: {score}",
            FONT_MEDIUM,
            WHITE,
            22,
            20
        )

        draw_text(
            SCREEN,
            f"NYAWA: {lives}",
            FONT_MEDIUM,
            PINK,
            220,
            20
        )

        draw_text(
            SCREEN,
            f"LEVEL: {level}",
            FONT_MEDIUM,
            CYAN,
            390,
            20
        )

        draw_text(
            SCREEN,
            f"REKOR: {high_score}",
            FONT_MEDIUM,
            YELLOW,
            585,
            20
        )

        # Gambar balok
        for brick in bricks:

            brick.draw(SCREEN)

        # Gambar power-up
        for item in powerups:

            item.draw(SCREEN)

        # Gambar paddle dan bola
        paddle.draw(SCREEN)
        ball.draw(SCREEN)

        if paddle.wide_timer > 0:

            draw_text(
                SCREEN,
                "POWER-UP PADDLE AKTIF",
                FONT_SMALL,
                GREEN,
                22,
                HEIGHT - 28
            )

        # Tampilan siap bermain
        if state == "ready":

            draw_text(
                SCREEN,
                "TEKAN SPACE UNTUK MULAI",
                FONT_BIG,
                WHITE,
                WIDTH // 2,
                HEIGHT // 2 + 35,
                center=True
            )

            draw_text(
                SCREEN,
                "Gerakkan paddle dengan A/D atau tombol panah",
                FONT_SMALL,
                MUTED,
                WIDTH // 2,
                HEIGHT // 2 + 78,
                center=True
            )

        # Tampilan pause
        elif state == "paused":

            draw_text(
                SCREEN,
                "PAUSE",
                FONT_BIG,
                YELLOW,
                WIDTH // 2,
                HEIGHT // 2,
                center=True
            )

            draw_text(
                SCREEN,
                "Tekan P untuk melanjutkan",
                FONT_MEDIUM,
                WHITE,
                WIDTH // 2,
                HEIGHT // 2 + 55,
                center=True
            )

        # Tampilan game over
        elif state == "lost":

            draw_text(
                SCREEN,
                "GAME OVER",
                FONT_BIG,
                RED,
                WIDTH // 2,
                HEIGHT // 2 - 25,
                center=True
            )

            draw_text(
                SCREEN,
                f"Skor akhir: {score}",
                FONT_MEDIUM,
                WHITE,
                WIDTH // 2,
                HEIGHT // 2 + 25,
                center=True
            )

            draw_text(
                SCREEN,
                "Tekan SPACE atau R untuk bermain lagi",
                FONT_SMALL,
                MUTED,
                WIDTH // 2,
                HEIGHT // 2 + 70,
                center=True
            )

        pygame.display.flip()

    pygame.quit()


# ==========================================
# MENJALANKAN PROGRAM
# ==========================================

if __name__ == "__main__":

    main()
