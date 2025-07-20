import pygame, random, sys

# Configurări
pygame.init()
WIDTH, HEIGHT = 480, 640
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 24)

# Culori
WHITE, BLACK, RED, BLUE = (255, 255, 255), (0, 0, 0), (200, 50, 50), (50, 100, 200)

# Personaj
player_size = 16
player = pygame.Rect(WIDTH//2, HEIGHT - 50, player_size, player_size)
player_speed = 4

# Blocuri
block_size = 32
blocks = []
spawn_patterns = ['line', 'zigzag', 'grid']
pattern_timer = pygame.time.get_ticks()
block_timer = pygame.time.get_ticks()
current_pattern = random.choice(spawn_patterns)
score = 0

def generate_block_positions(pattern):
    positions = []
    if pattern == 'line':
        for i in range(0, WIDTH, block_size):
            if random.random() > 0.2:  # ~80% șansă să apară un bloc
                positions.append(i)
    elif pattern == 'zigzag':
        for i in range(0, WIDTH, block_size*2):
            offset = block_size if (i//block_size) % 2 == 0 else 0
            positions.append(i + offset)
    elif pattern == 'grid':
        for i in range(0, WIDTH, block_size*2):
            if random.random() > 0.5:
                positions.append(i)
    return positions


# Joc
start_time = pygame.time.get_ticks()
running = True
while running:
    SCREEN.fill(BLACK)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Mișcare
    if keys[pygame.K_a] and player.left > 0: player.x -= player_speed
    if keys[pygame.K_d] and player.right < WIDTH: player.x += player_speed
    if keys[pygame.K_w] and player.top > 0: player.y -= player_speed
    if keys[pygame.K_s] and player.bottom < HEIGHT: player.y += player_speed

    current_time = pygame.time.get_ticks()

    # Schimbă pattern la 10 secunde
    if current_time - pattern_timer >= 10000:
        current_pattern = random.choice(spawn_patterns)
        pattern_timer = current_time

    # Generează blocuri la fiecare 1 secundă
    if current_time - block_timer >= 1000:
        positions = generate_block_positions(current_pattern)
        for x in positions:
            blocks.append(pygame.Rect(x, -block_size, block_size, block_size))
        block_timer = current_time

    # Mișcare blocuri
    for block in blocks[:]:
        block.y += 4
        if block.colliderect(player):
            SCREEN.fill(BLACK)
            text = FONT.render(f"Game Over! Scor: {score}", True, WHITE)
            SCREEN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            pygame.display.update()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()
        if block.y > HEIGHT:
            blocks.remove(block)
            score += 1

    # Desenare
    pygame.draw.rect(SCREEN, RED, player)
    for block in blocks:
        pygame.draw.rect(SCREEN, WHITE, block, 1)
        pygame.draw.rect(SCREEN, WHITE, block.inflate(-2, -2))

    # Afișare scor
    score_text = FONT.render(f"Scor: {score}", True, BLUE)
    SCREEN.blit(score_text, (10, 10))

    pygame.display.update()
    CLOCK.tick(60)
