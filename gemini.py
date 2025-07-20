import pygame
import random
import sys
import time

# --- Setări joc ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60
GAME_DURATION_FOR_PATTERN_CHANGE = 10  # secunde

# --- Culori (paletă pixel art limitată) ---
COLOR_BACKGROUND = (25, 25, 25)    # Gri închis aproape negru
COLOR_PLAYER = (255, 100, 100)  # Roșu deschis/rozaliu
COLOR_BLOCK = (100, 255, 100)   # Verde deschis
COLOR_OUTLINE = (50, 50, 50)    # Gri închis pentru contururi

# --- Proprietăți jucător ---
PLAYER_SIZE = 16
PLAYER_SPEED = 5

# --- Proprietăți blocuri ---
BLOCK_SIZE = 32
BLOCK_SPEED = 3
INITIAL_BLOCK_SPAWN_INTERVAL = 700  # milisecunde (mai lent la început)
MIN_BLOCK_SPAWN_INTERVAL = 200      # milisecunde (limita inferioară)
DIFFICULTY_INCREASE_INTERVAL = 50   # Cu cât scade intervalul la fiecare 50 de puncte acumulate

# --- Inițializare Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Evită Blocurile!")
clock = pygame.time.Clock()

# --- Font pentru scor și mesaje ---
font = pygame.font.Font(None, 48)

# --- Clasa Jucător ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(COLOR_PLAYER)
        pygame.draw.rect(self.image, COLOR_OUTLINE, self.image.get_rect(), 2) # Contur
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20

    def update(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED

        # Limitează mișcarea jucătorului la ecran
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# --- Clasa Bloc ---
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([BLOCK_SIZE, BLOCK_SIZE])
        self.image.fill(COLOR_BLOCK)
        pygame.draw.rect(self.image, COLOR_OUTLINE, self.image.get_rect(), 2) # Contur
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.passed = False # Flag pentru a verifica dacă blocul a trecut de jucător

    def update(self):
        self.rect.y += BLOCK_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Elimină blocul odată ce iese de pe ecran

# --- Funcții pentru generarea pattern-urilor ---
def generate_line_pattern(width, block_size, excluded_column=None):
    blocks = []
    num_blocks_x = width // block_size
    # Asigură-te că există o coloană liberă
    if excluded_column is None:
        excluded_column = random.randint(0, num_blocks_x - 1)
    for i in range(num_blocks_x):
        if i != excluded_column:
            blocks.append(i * block_size)
    return blocks

def generate_zigzag_pattern(width, block_size, current_step):
    blocks = []
    num_blocks_x = width // block_size
    
    # Calea liberă se mișcă de la stânga la dreapta și înapoi
    # Folosim modulo pentru a ne asigura că `step_in_row` rămâne în limite
    step_in_row = current_step % (num_blocks_x - 1) 
    
    # Direcția zigzagului (stanga-dreapta sau dreapta-stanga)
    if (current_step // (num_blocks_x - 1)) % 2 == 0: # Merge spre dreapta
        current_hole_col = step_in_row
    else: # Merge spre stanga
        current_hole_col = (num_blocks_x - 1) - step_in_row

    for i in range(num_blocks_x):
        if i != current_hole_col:
            blocks.append(i * block_size)
    return blocks

def generate_grid_pattern(width, block_size, density=0.3): # Redu densitatea implicită
    blocks = []
    num_blocks_x = width // block_size
    
    # Alege o coloană liberă aleatorie pentru a garanta o cale
    free_column = random.randint(0, num_blocks_x - 1)
    
    for i in range(num_blocks_x):
        if i == free_column: # Această coloană rămâne liberă
            continue
        if random.random() < density: # Altele au șansă să apară
            blocks.append(i * block_size)
    return blocks

# --- Funcție pentru a calcula intervalul curent de spawn ---
def get_current_spawn_interval(current_score):
    # Scade intervalul pe măsură ce scorul crește, dar nu sub MIN_BLOCK_SPAWN_INTERVAL
    reduction = (current_score // 50) * DIFFICULTY_INCREASE_INTERVAL
    new_interval = max(MIN_BLOCK_SPAWN_INTERVAL, INITIAL_BLOCK_SPAWN_INTERVAL - reduction)
    return new_interval

# --- Grupuri de sprite-uri ---
all_sprites = pygame.sprite.Group()
blocks = pygame.sprite.Group()

# --- Inițializare jucător ---
player = Player()
all_sprites.add(player)

# --- Variabile joc ---
score = 0
game_over = False
start_time = time.time()
last_pattern_change_time = time.time()
current_pattern = 0 # 0: linie, 1: zigzag, 2: grilă
last_block_spawn_time = pygame.time.get_ticks()

# --- Bucla jocului ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # Resetare joc
                game_over = False
                score = 0
                start_time = time.time()
                last_pattern_change_time = time.time()
                current_pattern = 0
                last_block_spawn_time = pygame.time.get_ticks()

                all_sprites.empty()
                blocks.empty()
                player = Player()
                all_sprites.add(player)


    if not game_over:
        current_time = time.time()

        # Schimbă pattern-ul la fiecare GAME_DURATION_FOR_PATTERN_CHANGE secunde
        if current_time - last_pattern_change_time >= GAME_DURATION_FOR_PATTERN_CHANGE:
            current_pattern = (current_pattern + 1) % 3 # Trece la următorul pattern
            last_pattern_change_time = current_time

        # Generează blocuri conform pattern-ului curent
        now = pygame.time.get_ticks()
        current_spawn_interval = get_current_spawn_interval(score) # Ia intervalul dinamic
        
        if now - last_block_spawn_time > current_spawn_interval:
            if current_pattern == 0: # Linie cu o gaură aleatorie
                excluded_col = random.randint(0, (SCREEN_WIDTH // BLOCK_SIZE) - 1)
                x_positions = generate_line_pattern(SCREEN_WIDTH, BLOCK_SIZE, excluded_col)
            elif current_pattern == 1: # Zigzag
                # Folosim o valoare discretă pentru current_step pentru a avea variație în zigzag
                x_positions = generate_zigzag_pattern(SCREEN_WIDTH, BLOCK_SIZE, int(current_time * 5)) # Multiplicator pentru a face zigzagul să progreseze
            else: # Grilă (apariție aleatorie, cu o cale garantată)
                x_positions = generate_grid_pattern(SCREEN_WIDTH, BLOCK_SIZE, density=0.3) 

            for x_pos in x_positions:
                new_block = Block(x_pos, -BLOCK_SIZE)
                all_sprites.add(new_block)
                blocks.add(new_block)
            last_block_spawn_time = now

        keys = pygame.key.get_pressed()
        player.update(keys)
        
        # Iterăm prin blocuri pentru a actualiza și a verifica dacă au fost evitate
        # Folosim list() pentru a evita erori de modificare a listei în timpul iterației
        for block in list(blocks): 
            block.update()
            # Verifică dacă blocul a trecut de partea de jos a jucătorului
            # și nu a fost deja marcat ca "trecut"
            if block.rect.top > player.rect.bottom and not block.passed:
                block.passed = True
                score += 1 # Creștem scorul pentru fiecare bloc evitat

        # Verifică coliziuni
        if pygame.sprite.spritecollideany(player, blocks):
            game_over = True

        # Desenare
        screen.fill(COLOR_BACKGROUND)
        all_sprites.draw(screen)

        # Afișează scorul
        score_text = font.render(f"Scor: {score}", True, COLOR_PLAYER)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)
    else:
        # Ecran Game Over
        screen.fill(COLOR_BACKGROUND)
        game_over_text = font.render("Game Over!", True, COLOR_PLAYER)
        score_final_text = font.render(f"Scorul tău: {score}", True, COLOR_PLAYER)
        restart_text = font.render("Apasa 'R' pentru a juca din nou", True, COLOR_OUTLINE)

        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        score_final_rect = score_final_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_final_text, score_final_rect)
        screen.blit(restart_text, restart_rect)
        pygame.display.flip()

pygame.quit()
sys.exit()