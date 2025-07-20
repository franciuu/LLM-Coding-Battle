import pygame, random, sys

# 🧱 Configurări inițiale
pygame.init()
WIDTH, HEIGHT = 480, 640
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 24)

# 🎨 Paletă limitată: negru, alb, roșu, albastru
WHITE, BLACK, RED, BLUE = (255, 255, 255), (0, 0, 0), (200, 50, 50), (50, 100, 200)

# 🎮 Setări personaj
player_size = 16
player = pygame.Rect(WIDTH//2, HEIGHT - 50, player_size, player_size)
player_speed = 4

# ⬇️ Blocuri și hartă procedurală
block_size = 32
blocks = []
spawn_patterns = ['line', 'zigzag', 'grid']
pattern_timer = 0
current_pattern = random.choice(spawn_patterns)
score = 0

def spawn_blocks(pattern):
    blocks.clear()
    if pattern == 'line':
        for i in range(0, WIDTH, block_size):
            blocks.append(pygame.Rect(i, -block_size, block_size, block_size))
    elif pattern == 'zigzag':
        for i in range(0, WIDTH, block_size*2):
            blocks.append(pygame.Rect(i + (block_size if i//block_size % 2 == 0 else 0), -block_size, block_size, block_size))
    elif pattern == 'grid':
        for i in range(0, WIDTH, block_size*2):
            for j in range(0, HEIGHT//4, block_size*2):
                blocks.append(pygame.Rect(i, -j, block_size, block_size))

# 🕹️ Loop principal
start_time = pygame.time.get_ticks()
while True:
    SCREEN.fill(BLACK)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 🧍 Mișcare personaj
    if keys[pygame.K_a] and player.left > 0: player.x -= player_speed
    if keys[pygame.K_d] and player.right < WIDTH: player.x += player_speed
    if keys[pygame.K_w] and player.top > 0: player.y -= player_speed
    if keys[pygame.K_s] and player.bottom < HEIGHT: player.y += player_speed

    # ⏱️ Schimbă pattern-ul la fiecare 10 secunde
    current_time = pygame.time.get_ticks()
    if current_time - pattern_timer > 10000:
        current_pattern = random.choice(spawn_patterns)
        spawn_blocks(current_pattern)
        pattern_timer = current_time

    # 🔽 Mișcare blocuri
    for block in blocks:
        block.y += 3
        if block.colliderect(player):
            SCREEN.fill(BLACK)
            text = FONT.render(f"Game Over! Scor: {score}", True, WHITE)
            SCREEN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            pygame.display.update()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()

    # 📈 Scor
    score = (current_time - start_time) // 1000
    score_text = FONT.render(f"Scor: {score}", True, BLUE)
    SCREEN.blit(score_text, (10, 10))

    # 🖼️ Desenare personaje
    pygame.draw.rect(SCREEN, RED, player)
    for block in blocks:
        pygame.draw.rect(SCREEN, WHITE, block, 1)  # Contur alb
        pygame.draw.rect(SCREEN, WHITE, block.inflate(-2, -2))  # Umplere ușoară

    pygame.display.update()
    CLOCK.tick(60)
