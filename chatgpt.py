import pygame
import random
import sys

# Inițializare Pygame
pygame.init()

# Configurări fereastră
WIDTH, HEIGHT = 320, 240
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Dodge")

# Culori (paletă de 4 culori)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 30, 30)
BLUE = (50, 90, 200)

# Clock & font
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# Player
player_size = 16
player_speed = 3
player = pygame.Rect(WIDTH // 2, HEIGHT - 40, player_size, player_size)

# Blocuri
block_size = 32
block_speed = 2
blocks = []

# Patternuri de generare
patterns = ['line', 'zigzag', 'grid']
current_pattern = random.choice(patterns)
pattern_timer = 0

# Timp și scor
start_ticks = pygame.time.get_ticks()
score = 0
game_over = False

def draw_player():
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.rect(screen, BLACK, player, 1)  # contur

def draw_block(block):
    pygame.draw.rect(screen, RED, block)
    pygame.draw.rect(screen, BLACK, block, 1)  # contur

def spawn_blocks(pattern):
    blocks = []
    if pattern == 'line':
        for i in range(0, WIDTH, block_size):
            blocks.append(pygame.Rect(i, -block_size, block_size, block_size))
    elif pattern == 'zigzag':
        for i in range(0, WIDTH, block_size * 2):
            offset = (block_size if (pygame.time.get_ticks() // 500) % 2 == 0 else 0)
            blocks.append(pygame.Rect(i + offset, -block_size, block_size, block_size))
    elif pattern == 'grid':
        for i in range(0, WIDTH, block_size * 2):
            if random.random() > 0.5:
                blocks.append(pygame.Rect(i, -block_size, block_size, block_size))
    return blocks

def reset_game():
    global blocks, player, score, start_ticks, current_pattern
    player.x = WIDTH // 2
    player.y = HEIGHT - 40
    blocks = []
    score = 0
    start_ticks = pygame.time.get_ticks()
    current_pattern = random.choice(patterns)

# Loop principal
spawn_delay = 1000
last_spawn = pygame.time.get_ticks()

while True:
    dt = clock.tick(60)
    screen.fill(BLUE)

    # Timp și scor
    seconds = (pygame.time.get_ticks() - start_ticks) / 1000
    score = int(seconds)

    if pygame.time.get_ticks() - pattern_timer > 10000:
        current_pattern = random.choice(patterns)
        pattern_timer = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Control player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player.y -= player_speed
    if keys[pygame.K_s]: player.y += player_speed
    if keys[pygame.K_a]: player.x -= player_speed
    if keys[pygame.K_d]: player.x += player_speed

    # Constrângere în ecran
    player.clamp_ip(screen.get_rect())

    # Generare blocuri
    if pygame.time.get_ticks() - last_spawn > spawn_delay:
        blocks.extend(spawn_blocks(current_pattern))
        last_spawn = pygame.time.get_ticks()

    # Update blocuri
    for block in blocks:
        block.y += block_speed
        draw_block(block)

    # Eliminare blocuri ieșite din ecran
    blocks = [b for b in blocks if b.y < HEIGHT]

    # Coliziuni
    for block in blocks:
        if player.colliderect(block):
            game_over = True
            break

    # Desenează playerul
    draw_player()

    # Text scor
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Game over
    if game_over:
        game_over_text = font.render(f"Game Over! Score: {score}", True, BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - 60, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        reset_game()
        game_over = False

    pygame.display.flip()
