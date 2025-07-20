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
INITIAL_BLOCK_SPEED = 3

# Paleta de culori (4 culori + efecte)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)  # Pentru power-ups

# Stări joc
MENU = 0
GAME = 1
GAME_OVER = 2

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.randint(-8, 8)
        self.vel_y = random.randint(-8, 8)
        self.life = 30  # Frames de viață
        self.size = random.randint(2, 4)
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.3  # Gravitate
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = self.life / 30.0
            color_intensity = int(255 * alpha)
            color = (color_intensity, color_intensity, color_intensity)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
    
    def is_dead(self):
        return self.life <= 0

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = 2
        self.type = 'invincible'  # Momentan doar invincibilitate
        self.pulse = 0
        
    def update(self):
        self.y += self.speed
        self.pulse += 0.2
        
    def draw(self, screen):
        # Efect de puls
        pulse_size = self.size + int(math.sin(self.pulse) * 3)
        pygame.draw.rect(screen, GREEN, (self.x, self.y, pulse_size, pulse_size))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, pulse_size, pulse_size), 2)
        # Simbol "+" pentru power-up
        pygame.draw.line(screen, BLACK, (self.x + pulse_size//2 - 4, self.y + pulse_size//2),
                        (self.x + pulse_size//2 + 4, self.y + pulse_size//2), 2)
        pygame.draw.line(screen, BLACK, (self.x + pulse_size//2, self.y + pulse_size//2 - 4),
                        (self.x + pulse_size//2, self.y + pulse_size//2 + 4), 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.invincible = False
        self.invincible_timer = 0
        self.flash_timer = 0
        
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
            
        # Actualizează invincibilitatea
        if self.invincible:
            self.invincible_timer -= 1
            self.flash_timer += 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def draw(self, screen):
        # Flash effect când e invincibil
        if self.invincible and (self.flash_timer // 5) % 2 == 0:
            return  # Nu desenează pentru efect flash
            
        # Desenează personajul
        color = GREEN if self.invincible else WHITE
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.size, self.size), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
        
    def activate_invincibility(self, duration_frames):
        self.invincible = True
        self.invincible_timer = duration_frames
        self.flash_timer = 0

class Block:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.size = BLOCK_SIZE
        self.speed = speed
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
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
        
        if self.pattern_timer >= 10000:
            self.current_pattern = (self.current_pattern + 1) % len(self.patterns)
            self.pattern_timer = 0
            
    def should_spawn_block(self):
        if self.spawn_timer >= 1000:
            self.spawn_timer = 0
            return True
        return False
        
    def get_spawn_positions(self):
        pattern = self.patterns[self.current_pattern]
        positions = []
        
        if pattern == 'line':
            x = random.randint(0, SCREEN_WIDTH - BLOCK_SIZE)
            positions.append(x)
        elif pattern == 'zigzag':
            time_factor = pygame.time.get_ticks() / 1000.0
            x = int((SCREEN_WIDTH / 2) + math.sin(time_factor) * 200)
            x = max(0, min(x, SCREEN_WIDTH - BLOCK_SIZE))
            positions.append(x)
        elif pattern == 'grid':
            for i in range(0, SCREEN_WIDTH, BLOCK_SIZE * 3):
                if random.random() < 0.6:
                    positions.append(i)
        elif pattern == 'wave':
            time_factor = pygame.time.get_ticks() / 500.0
            for i in range(3):
                x = int((SCREEN_WIDTH / 4) * (i + 1) + math.sin(time_factor + i) * 50)
                x = max(0, min(x, SCREEN_WIDTH - BLOCK_SIZE))
                positions.append(x)
        else:  # random
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
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.state = MENU
        self.reset_game()
        
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.blocks = []
        self.particles = []
        self.powerups = []
        self.pattern_gen = PatternGenerator()
        
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.current_speed = INITIAL_BLOCK_SPEED
        self.speed_increase_timer = 0
        self.powerup_spawn_timer = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif self.state == MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GAME
                        self.reset_game()
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.state = MENU
                    elif event.key == pygame.K_r:
                        self.state = GAME
                        self.reset_game()
        return True
        
    def update_menu(self):
        pass  # Meniul nu necesită actualizări
        
    def update_game(self):
        keys = pygame.key.get_pressed()
        dt = self.clock.get_time()
        
        # Actualizează personajul
        self.player.update(keys)
        
        # Actualizează timer-ul de viteză (30 secunde = 30000ms)
        self.speed_increase_timer += dt
        if self.speed_increase_timer >= 30000:
            self.current_speed += 1
            self.speed_increase_timer = 0
        
        # Actualizează generatorul de pattern-uri
        self.pattern_gen.update(dt)
        
        # Spawnează blocuri noi
        if self.pattern_gen.should_spawn_block():
            positions = self.pattern_gen.get_spawn_positions()
            for x in positions:
                self.blocks.append(Block(x, -BLOCK_SIZE, self.current_speed))
        
        # Spawnează power-ups (la fiecare 15 secunde)
        self.powerup_spawn_timer += dt
        if self.powerup_spawn_timer >= 15000:
            if random.random() < 0.7:  # 70% șansă
                x = random.randint(0, SCREEN_WIDTH - 20)
                self.powerups.append(PowerUp(x, -20))
            self.powerup_spawn_timer = 0
        
        # Actualizează blocurile
        for block in self.blocks[:]:
            block.update()
            if block.is_off_screen():
                self.blocks.remove(block)
                
        # Actualizează power-ups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_off_screen():
                self.powerups.remove(powerup)
                
        # Actualizează particulele
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
        
        # Verifică coliziunile cu power-ups
        player_rect = self.player.get_rect()
        for powerup in self.powerups[:]:
            if player_rect.colliderect(powerup.get_rect()):
                if powerup.type == 'invincible':
                    self.player.activate_invincibility(180)  # 3 secunde la 60 FPS
                self.powerups.remove(powerup)
                break
        
        # Verifică coliziunile cu blocurile
        if not self.player.invincible:
            for block in self.blocks:
                if player_rect.colliderect(block.get_rect()):
                    # Creează particule de impact
                    for _ in range(15):
                        self.particles.append(Particle(self.player.x + PLAYER_SIZE//2, 
                                                     self.player.y + PLAYER_SIZE//2))
                    self.state = GAME_OVER
                    break
                    
        # Calculează scorul
        self.score = (pygame.time.get_ticks() - self.start_time) // 1000
        
    def update_game_over(self):
        # Actualizează particulele și după Game Over pentru efect
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
        
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title_text = self.font_large.render("EVITĂ BLOCURILE", True, WHITE)
        start_text = self.font_medium.render("Apasă SPACE pentru a începe", True, WHITE)
        controls_text = self.font_small.render("Controluri: WASD", True, GRAY)
        quit_text = self.font_small.render("ESC pentru ieșire", True, GRAY)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(start_text, start_rect)
        self.screen.blit(controls_text, controls_rect)
        self.screen.blit(quit_text, quit_rect)
        
    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Desenează toate obiectele jocului
        self.player.draw(self.screen)
        for block in self.blocks:
            block.draw(self.screen)
        for powerup in self.powerups:
            powerup.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
            
        # UI
        score_text = self.font_medium.render(f"Scor: {self.score}", True, WHITE)
        speed_text = self.font_small.render(f"Viteză: {self.current_speed}", True, WHITE)
        pattern_text = self.font_small.render(f"Pattern: {self.pattern_gen.patterns[self.pattern_gen.current_pattern]}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(speed_text, (10, 45))
        self.screen.blit(pattern_text, (10, 70))
        
        # Afișează timer invincibilitate
        if self.player.invincible:
            inv_time = self.player.invincible_timer / 60.0
            inv_text = self.font_small.render(f"Invincibil: {inv_time:.1f}s", True, GREEN)
            self.screen.blit(inv_text, (SCREEN_WIDTH - 150, 10))
        
    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        # Desenează particulele care rămân
        for particle in self.particles:
            particle.draw(self.screen)
            
        game_over_text = self.font_large.render("GAME OVER", True, WHITE)
        final_score_text = self.font_medium.render(f"Scor Final: {self.score}", True, WHITE)
        restart_text = self.font_small.render("SPACE - Meniu | R - Restart", True, GRAY)
        quit_text = self.font_small.render("ESC - Ieșire", True, GRAY)
        
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(final_score_text, final_score_rect)
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(quit_text, quit_rect)
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            # Actualizare bazată pe stare
            if self.state == MENU:
                self.update_menu()
            elif self.state == GAME:
                self.update_game()
            elif self.state == GAME_OVER:
                self.update_game_over()
            
            # Desenare bazată pe stare
            if self.state == MENU:
                self.draw_menu()
            elif self.state == GAME:
                self.draw_game()
            elif self.state == GAME_OVER:
                self.draw_game_over()
                
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

# Rulează jocul
if __name__ == "__main__":
    game = Game()
    game.run()