import pygame
import random
import math
import sys

# Inițializare Pygame
pygame.init()

# Constante
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 16
BLOCK_SIZE = 32
PLAYER_SPEED = 5
BLOCK_SPEED = 3

# Paleta de culori (4 culori)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        
    def update(self, keys):
        # Controlul WASD
        if keys[pygame.K_w] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y < SCREEN_HEIGHT - self.size:
            self.y += self.speed
        if keys[pygame.K_a] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < SCREEN_WIDTH - self.size:
            self.x += self.speed
    
    def draw(self, screen):
        # Desenează personajul ca un pătrat pixelat cu contur
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.size, self.size), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = BLOCK_SIZE
        self.speed = BLOCK_SPEED
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        # Desenează blocul cu contur
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.size, self.size), 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class PatternGenerator:
    def __init__(self):
        self.patterns = ['line', 'zigzag', 'grid', 'random', 'wave']
        self.current_pattern = 0
        self.pattern_timer = 0
        self.spawn_timer = 0
        
    def update(self, dt):
        self.pattern_timer += dt
        self.spawn_timer += dt
        
        # Schimbă pattern-ul la fiecare 10 secunde
        if self.pattern_timer >= 10000:  # 10 secunde în milisecunde
            self.current_pattern = (self.current_pattern + 1) % len(self.patterns)
            self.pattern_timer = 0
            
    def should_spawn_block(self):
        # Spawnează blocuri la intervale regulate
        if self.spawn_timer >= 1000:  # 1 secundă
            self.spawn_timer = 0
            return True
        return False
        
    def get_spawn_positions(self):
        pattern = self.patterns[self.current_pattern]
        positions = []
        
        if pattern == 'line':
            # O linie de blocuri
            x = random.randint(0, SCREEN_WIDTH - BLOCK_SIZE)
            positions.append(x)
            
        elif pattern == 'zigzag':
            # Pattern zigzag
            time_factor = pygame.time.get_ticks() / 1000.0
            x = int((SCREEN_WIDTH / 2) + math.sin(time_factor) * 200)
            x = max(0, min(x, SCREEN_WIDTH - BLOCK_SIZE))
            positions.append(x)
            
        elif pattern == 'grid':
            # Grilă cu spații
            for i in range(0, SCREEN_WIDTH, BLOCK_SIZE * 3):
                if random.random() < 0.6:  # 60% șansă să apară bloc
                    positions.append(i)
                    
        elif pattern == 'wave':
            # Pattern în undă
            time_factor = pygame.time.get_ticks() / 500.0
            for i in range(3):
                x = int((SCREEN_WIDTH / 4) * (i + 1) + math.sin(time_factor + i) * 50)
                x = max(0, min(x, SCREEN_WIDTH - BLOCK_SIZE))
                positions.append(x)
                
        else:  # random
            # Pattern aleatoriu
            num_blocks = random.randint(1, 4)
            for _ in range(num_blocks):
                x = random.randint(0, SCREEN_WIDTH - BLOCK_SIZE)
                positions.append(x)
                
        return positions

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Evită Blocurile - Joc Minimalist")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Inițializează obiectele jocului
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.blocks = []
        self.pattern_gen = PatternGenerator()
        
        # Scor și timp
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.game_over = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        return True
        
    def update(self):
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        dt = self.clock.get_time()
        
        # Actualizează personajul
        self.player.update(keys)
        
        # Actualizează generatorul de pattern-uri
        self.pattern_gen.update(dt)
        
        # Spawnează blocuri noi
        if self.pattern_gen.should_spawn_block():
            positions = self.pattern_gen.get_spawn_positions()
            for x in positions:
                self.blocks.append(Block(x, -BLOCK_SIZE))
        
        # Actualizează blocurile
        for block in self.blocks[:]:
            block.update()
            if block.is_off_screen():
                self.blocks.remove(block)
                
        # Verifică coliziunile
        player_rect = self.player.get_rect()
        for block in self.blocks:
            if player_rect.colliderect(block.get_rect()):
                self.game_over = True
                break
                
        # Calculează scorul (timp supraviețuit în secunde)
        self.score = (pygame.time.get_ticks() - self.start_time) // 1000
        
    def draw(self):
        # Fundal negru
        self.screen.fill(BLACK)
        
        # Desenează personajul și blocurile
        self.player.draw(self.screen)
        for block in self.blocks:
            block.draw(self.screen)
            
        # Afișează scorul și pattern-ul curent
        score_text = self.font.render(f"Scor: {self.score}", True, WHITE)
        pattern_text = self.font.render(f"Pattern: {self.pattern_gen.patterns[self.pattern_gen.current_pattern]}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(pattern_text, (10, 50))
        
        # Afișează Game Over dacă e cazul
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            final_score_text = self.font.render(f"Scor Final: {self.score}", True, WHITE)
            restart_text = self.font.render("Apasă ESC pentru ieșire", True, GRAY)
            
            # Centrează textele
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(final_score_text, final_score_rect)
            self.screen.blit(restart_text, restart_rect)
            
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
            
        pygame.quit()
        sys.exit()

# Rulează jocul
if __name__ == "__main__":
    game = Game()
    game.run()