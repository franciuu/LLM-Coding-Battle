import pygame
import random
import time

# Setări ecran
WIDTH, HEIGHT = 320, 480
FPS = 60

# Paletă maxim 4 culori
COLOR_BG     = (  0,   0,   0)   # fundal
COLOR_PLAYER = (255, 255, 255)   # player
COLOR_BLOCK  = (200,   0,   0)   # blocuri
COLOR_OUTL   = ( 40,  40,  40)   # contur

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
active_spawn_rows = []  # Listă cu referință la fiecare rând de blocuri spawnat pentru scor

spawn_timer = 0
pattern_timer = 0
current_pattern = 0  # 0=linie, 1=zigzag, 2=grid

def draw_pixel_rect(surface, color, rect):
    pygame.draw.rect(surface, COLOR_OUTL, rect)
    pygame.draw.rect(surface, color, rect.inflate(-2, -2))

def spawn_line_pattern():
    blocks_row = []
    num_blocks = WIDTH // BLOCK_SIZE
    gap_index = random.randint(0, num_blocks - 1)
    for i in range(num_blocks):
        if i != gap_index:
            block = pygame.Rect(i * BLOCK_SIZE, -BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            blocks_row.append(block)
    return blocks_row, gap_index

def spawn_zigzag_pattern():
    blocks_row = []
    num_blocks = WIDTH // BLOCK_SIZE
    offset = (pygame.time.get_ticks() // 800) % 2 * (BLOCK_SIZE // 2)
    gap_index = random.randint(0, num_blocks - 1)
    for i in range(num_blocks):
        xpos = int((i * BLOCK_SIZE + offset) % (WIDTH - BLOCK_SIZE + 1))
        if i != gap_index:
            block = pygame.Rect(xpos, -BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            blocks_row.append(block)
    return blocks_row, gap_index

def spawn_grid_pattern():
    blocks_row = []
    num_blocks_x = WIDTH // BLOCK_SIZE
    num_blocks_y = 2  # două linii
    gaps = [random.randint(0, num_blocks_x - 1) for _ in range(num_blocks_y)]
    for row in range(num_blocks_y):
        for i in range(num_blocks_x):
            if i != gaps[row]:
                block = pygame.Rect(i * BLOCK_SIZE, -BLOCK_SIZE * (row + 1) - 10 * row, BLOCK_SIZE, BLOCK_SIZE)
                blocks_row.append(block)
    return blocks_row, gaps

def check_row_evaded(row_blocks, player):
    # Verifică dacă toate blocurile din row_blocks au trecut de player fără coliziune
    for block in row_blocks:
        if player.colliderect(block):
            return False  # A existat o coliziune
        if block.bottom >= player.top and not player.colliderect(block):
            continue
    return True

def is_row_dead(row_blocks):
    # Toate blocurile din row_blocks au ieșit de pe ecran
    return all(b.top >= HEIGHT for b in row_blocks)

score = 0
game_over = False

start_time = time.time()

while not game_over:
    dt = clock.tick(FPS)
    time_now = pygame.time.get_ticks()
    screen.fill(COLOR_BG)

    # Schimbă pattern-ul la fiecare 10 secunde
    if time_now - pattern_timer >= 10000:
        pattern_timer = time_now
        current_pattern = (current_pattern + 1) % 3

    # Spawning blocuri – păstrează și gruparea lor pe rând
    if time_now - spawn_timer > 800:
        if current_pattern == 0:  # Linie cu gap
            new_row, _ = spawn_line_pattern()
        elif current_pattern == 1:  # Zigzag cu gap
            new_row, _ = spawn_zigzag_pattern()
        else:  # Grid cu câte un gap pe fiecare rând
            new_row, _ = spawn_grid_pattern()
        if new_row:
            blocks.extend(new_row)
            active_spawn_rows.append(list(new_row))  # referință pentru acest rând
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

    # Mișcare blocuri & desenare
    for block in blocks:
        block.y += block_speed
    blocks = [b for b in blocks if b.top < HEIGHT]
    for block in blocks:
        draw_pixel_rect(screen, COLOR_BLOCK, block)
        if player.colliderect(block):
            game_over = True

    # Player
    draw_pixel_rect(screen, COLOR_PLAYER, player)

    # Actualizare scor: increment doar când playerul a evitat un "row" întreg (toate blocurile din row au trecut sub player fără coliziune)
    for row in list(active_spawn_rows):
        if is_row_dead(row):
            # Dacă nu a existat coliziune, adaugă la scor pentru fiecare bloc evitat din acest rând
            if check_row_evaded(row, player):
                score += len(row)
            active_spawn_rows.remove(row)

    # Scor
    scrtxt = font.render(f"Score: {score}", True, COLOR_PLAYER)
    screen.blit(scrtxt, (10, 8))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

# Game Over – ecran final
screen.fill(COLOR_BG)
overtext = font.render("Game Over!", True, COLOR_PLAYER)
scoretxt = font.render(f"Scor final: {score}", True, COLOR_PLAYER)
screen.blit(overtext, (WIDTH // 2 - overtext.get_width() // 2, HEIGHT // 2 - 16))
screen.blit(scoretxt, (WIDTH // 2 - scoretxt.get_width() // 2, HEIGHT // 2 + 10))
pygame.display.flip()
pygame.time.wait(600)
pygame.quit()
