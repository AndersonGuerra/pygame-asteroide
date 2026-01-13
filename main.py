import pygame
import random
import math

pygame.init()

# ================= CONFIG =================
WIDTH, HEIGHT = 900, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 64)

# ================= FUNÇÕES =================
def wrap_position(pos):
    return pygame.Vector2(pos.x % WIDTH, pos.y % HEIGHT)

def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

# ================= NAVE =================
class Ship:
    def __init__(self):
        self.radius = 12
        self.reset()

    def reset(self):
        self.pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0
        self.invincible = 120  # frames de invencibilidade

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.angle += 4
        if keys[pygame.K_RIGHT]:
            self.angle -= 4
        if keys[pygame.K_UP]:
            direction = pygame.Vector2(1, 0).rotate(-self.angle)
            self.vel += direction * 0.25

        self.pos += self.vel
        self.vel *= 0.99
        self.pos = wrap_position(self.pos)

        if self.invincible > 0:
            self.invincible -= 1

    def draw(self):
        if self.invincible > 0 and self.invincible % 10 < 5:
            return

        tip = pygame.Vector2(20, 0).rotate(-self.angle)
        left = pygame.Vector2(-10, 8).rotate(-self.angle)
        right = pygame.Vector2(-10, -8).rotate(-self.angle)

        points = [
            self.pos + tip,
            self.pos + left,
            self.pos + right
        ]

        pygame.draw.polygon(screen, WHITE, points, 2)

# ================= TIRO =================
class Bullet:
    def __init__(self, pos, angle):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(1, 0).rotate(-angle) * 8
        self.life = 60

    def update(self):
        self.pos += self.vel
        self.pos = wrap_position(self.pos)
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, WHITE, self.pos, 2)

# ================= ASTEROIDE =================
class Asteroid:
    def __init__(self, pos=None, size=3):
        self.size = size
        self.radius = size * 15
        self.pos = pos if pos else pygame.Vector2(
            random.randrange(WIDTH),
            random.randrange(HEIGHT)
        )
        angle = random.uniform(0, 360)
        speed = random.uniform(1, 3)
        self.vel = pygame.Vector2(1, 0).rotate(angle) * speed

    def update(self):
        self.pos += self.vel
        self.pos = wrap_position(self.pos)

    def draw(self):
        pygame.draw.circle(screen, WHITE, self.pos, self.radius, 2)

# ================= HUD =================
def draw_hud(lives, score):
    lives_text = font.render(f"Vidas: {lives}", True, WHITE)
    score_text = font.render(f"Pontos: {score}", True, WHITE)

    screen.blit(lives_text, (20, 20))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))

def draw_game_over(score):
    text = big_font.render("GAME OVER", True, RED)
    score_text = font.render(f"Pontuação final: {score}", True, WHITE)

    screen.blit(
        text,
        (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - 50)
    )
    screen.blit(
        score_text,
        (WIDTH / 2 - score_text.get_width() / 2, HEIGHT / 2 + 20)
    )

# ================= JOGO =================
ship = Ship()
bullets = []
asteroids = [Asteroid(size=3) for _ in range(5)]

lives = 3
score = 0
game_over = False

running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                bullets.append(Bullet(ship.pos, ship.angle))

    keys = pygame.key.get_pressed()

    if not game_over:
        ship.update(keys)

        for bullet in bullets[:]:
            bullet.update()
            if bullet.life <= 0:
                bullets.remove(bullet)

        for asteroid in asteroids:
            asteroid.update()

        # Colisão tiro x asteroide
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if distance(bullet.pos, asteroid.pos) < asteroid.radius:
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)

                    if asteroid.size == 3:
                        score += 20
                    elif asteroid.size == 2:
                        score += 50
                    else:
                        score += 100

                    if asteroid.size > 1:
                        for _ in range(2):
                            asteroids.append(
                                Asteroid(asteroid.pos, asteroid.size - 1)
                            )
                    break

        # Colisão nave x asteroide
        if ship.invincible == 0:
            for asteroid in asteroids:
                if distance(ship.pos, asteroid.pos) < asteroid.radius + ship.radius:
                    lives -= 1
                    ship.reset()
                    if lives <= 0:
                        game_over = True
                    break

        # Recria asteroides se acabar
        if not asteroids:
            asteroids = [Asteroid(size=3) for _ in range(5)]

    # Desenho
    ship.draw()
    for bullet in bullets:
        bullet.draw()
    for asteroid in asteroids:
        asteroid.draw()

    draw_hud(lives, score)

    if game_over:
        draw_game_over(score)

    pygame.display.flip()

pygame.quit()