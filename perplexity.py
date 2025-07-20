import pygame
import random
import time

# Setări ecran
WIDTH, HEIGHT = 320, 480
FPS = 60

# Paletă: MAXIM 4 culori
BLACK   = (  0,   0,   0)  # fundal
WHITE   = (255, 255, 255)  # player
RED     = (200,   0,   0)  # blocuri
OUTLINE = ( 40,  40,  40)  # contururi

# Init Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Dodger")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Player
PLAYER_SIZE = 16
player = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT - PLAYER_SIZE - 8, PLAYER_SIZE, PLAYER_SIZE)
player_speed = 5

# Blocuri
BLOCK_SIZE = 32
block_speed = 3
blocks = []
spawn_timer = 0
pattern_timer = 0
current_pattern = 0  # 0=linie, 1=zig-zag, 2=grid

def draw_pixel_rect(surface, color, rect):
    pygame.draw.rect(surface, OUTLINE, rect)
    pygame.draw.rect(surface, color, rect.inflate(-2, -2))

def spawn_blocks(pattern):
    new_blocks = []
    if pattern == 0:  # Linie
        x_start = random.randint(0, (WIDTH - BLOCK_SIZE) // (BLOCK_SIZE + 4)) * (BLOCK_SIZE + 4)
        for x in range(0, WIDTH, BLOCK_SIZE + 4):
            new_blocks.append(pygame.Rect(x, -BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    elif pattern == 1:  # Zig-zag
        offset = (pygame.time.get_ticks() // 800) % 2 * (BLOCK_SIZE // 2)
        for i in range(0, WIDTH, BLOCK_SIZE + 4):
            xpos = (i + offset) % (WIDTH - BLOCK_SIZE)
            new_blocks.append(pygame.Rect(xpos, -BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    elif pattern == 2:  # Grid
        for x in range(0, WIDTH, BLOCK_SIZE + 4):
            for y in (-BLOCK_SIZE, -2*BLOCK_SIZE-10):
                new_blocks.append(pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))
    return new_blocks

# Start timp și scor
start_time = time.time()
game_over = False
score = 0

while not game_over:
    dt = clock.tick(FPS)
    time_now = pygame.time.get_ticks()
    screen.fill(BLACK)

    # Pattern schimbat la fiecare 10 secunde
    if time_now - pattern_timer >= 10000:
        pattern_timer = time_now
        current_pattern = (current_pattern + 1) % 3

    # Blocuri noi la interval
    if time_now - spawn_timer > 800:
        blocks.extend(spawn_blocks(current_pattern))
        spawn_timer = time_now

    # Controale WASD
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player.top > 0:
        player.y -= player_speed
    if keys[pygame.K_s] and player.bottom < HEIGHT:
        player.y += player_speed
    if keys[pygame.K_a] and player.left > 0:
        player.x -= player_speed
    if keys[pygame.K_d] and player.right < WIDTH:
        player.x += player_speed

    # Mișcare blocuri și coliziuni
    for block in blocks:
        block.y += block_speed
    blocks = [b for b in blocks if b.top < HEIGHT]
    for block in blocks:
        draw_pixel_rect(screen, RED, block)
        if player.colliderect(block):
            game_over = True

    # Player
    draw_pixel_rect(screen, WHITE, player)

    # Scor
    score = int(time.time() - start_time)
    scrtxt = font.render(f"Score: {score}", True, WHITE)
    screen.blit(scrtxt, (10, 8))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

# GAME OVER - ecran final
screen.fill(BLACK)
overtext = font.render("Game Over!", True, WHITE)
scoretxt = font.render(f"Scor final: {score}", True, WHITE)
screen.blit(overtext, (WIDTH // 2 - overtext.get_width() // 2, HEIGHT // 2 - 16))
screen.blit(scoretxt, (WIDTH // 2 - scoretxt.get_width() // 2, HEIGHT // 2 + 10))
pygame.display.flip()
pygame.time.wait(3000)
pygame.quit()
