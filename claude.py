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
PLAYER_SPEED = 3
INITIAL_BLOCK_SPEED = 3
GRID_COLUMNS = 20  # Numărul de coloane în grid-ul virtual
COLUMN_WIDTH = SCREEN_WIDTH // GRID_COLUMNS
MAX_SIMULTANEOUS_BLOCKS = 15  

# Paleta de culori extinsă
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)
BLUE = (100, 150, 255)  # Pentru Shield
YELLOW = (255, 255, 0)  # Pentru Slow Time
GOLD = (255, 215, 0)    # Pentru Double Points
RED = (255, 100, 100)   # Pentru inimi

# Stări joc
MENU = 0
GAME = 1
GAME_OVER = 2

# Tipuri Power-ups
POWERUP_SHIELD = 0
POWERUP_SLOW = 1
POWERUP_DOUBLE = 2

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.randint(-8, 8)
        self.vel_y = random.randint(-8, 8)
        self.life = 30
        self.size = random.randint(2, 4)
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.3
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = self.life / 30.0
            color_intensity = int(255 * alpha)
            color = (color_intensity, color_intensity, color_intensity)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
    
    def is_dead(self):
        return self.life <= 0

class Block:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.size = BLOCK_SIZE
        self.speed = speed
        self.column = x // COLUMN_WIDTH  # Coloana pe care se află blocul
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.size, self.size), 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def is_completely_off_screen(self):
        """Verifică dacă blocul a trecut COMPLET de marginea inferioară"""
        return self.y > SCREEN_HEIGHT

class PowerUp(Block):  # Moștenește din Block pentru DRY principle
    def __init__(self, x, y, powerup_type, speed):
        super().__init__(x, y, speed)
        self.size = 24
        self.type = powerup_type
        self.pulse = 0
        
    def update(self):
        super().update()  # Folosește logica de mișcare din Block
        self.pulse += 0.15
        
    def draw(self, screen):
        # Efect de puls
        pulse_offset = int(math.sin(self.pulse) * 2)
        current_size = self.size + pulse_offset
        
        # Culoare bazată pe tip
        if self.type == POWERUP_SHIELD:
            color = BLUE
        elif self.type == POWERUP_SLOW:
            color = YELLOW
        else:  # POWERUP_DOUBLE
            color = GOLD
            
        # Desenează background-ul power-up-ului
        pygame.draw.rect(screen, color, (self.x, self.y, current_size, current_size))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, current_size, current_size), 2)
        
        # Desenează iconița specifică
        center_x = self.x + current_size // 2
        center_y = self.y + current_size // 2
        
        if self.type == POWERUP_SHIELD:
            # Desenează scut
            points = [
                (center_x, center_y - 6),
                (center_x - 4, center_y - 2),
                (center_x - 4, center_y + 2),
                (center_x, center_y + 6),
                (center_x + 4, center_y + 2),
                (center_x + 4, center_y - 2)
            ]
            pygame.draw.polygon(screen, BLACK, points, 2)
            
        elif self.type == POWERUP_SLOW:
            # Desenează ceas
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 6, 2)
            pygame.draw.line(screen, BLACK, (center_x, center_y), (center_x, center_y - 4), 2)
            pygame.draw.line(screen, BLACK, (center_x, center_y), (center_x + 3, center_y), 2)
            
        else:  # POWERUP_DOUBLE
            # Desenează stea
            star_points = []
            for i in range(10):
                angle = i * math.pi / 5
                if i % 2 == 0:
                    radius = 6
                else:
                    radius = 3
                x = center_x + radius * math.cos(angle - math.pi/2)
                y = center_y + radius * math.sin(angle - math.pi/2)
                star_points.append((x, y))
            pygame.draw.polygon(screen, BLACK, star_points)

class GridManager:
    """Gestionează grid-ul virtual pentru a evita suprapunerea blocurilor"""
    def __init__(self):
        self.occupied_columns = set()
        
    def get_free_columns(self):
        """Returnează coloanele libere"""
        all_columns = set(range(GRID_COLUMNS))
        return list(all_columns - self.occupied_columns)
    
    def occupy_column(self, column):
        """Marchează o coloană ca ocupată"""
        self.occupied_columns.add(column)
    
    def free_column(self, column):
        """Eliberează o coloană"""
        self.occupied_columns.discard(column)
    
    def update_from_blocks(self, blocks):
        """Actualizează grid-ul bazat pe blocurile active"""
        self.occupied_columns.clear()
        for block in blocks:
            # Consideră o coloană ocupată dacă blocul e încă în partea de sus a ecranului
            if block.y < SCREEN_HEIGHT // 3:
                column = int(block.x // COLUMN_WIDTH)
                self.occupied_columns.add(column)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = int(PLAYER_SIZE * 0.9)  # Reducere hitbox cu 10%
        self.visual_size = PLAYER_SIZE  # Păstrează dimensiunea vizuală
        self.speed = PLAYER_SPEED
        self.hp = 3
        self.max_hp = 3
        
        # Power-up states
        self.shield_active = False
        self.shield_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.flash_timer = 0
        
        # Pentru tracking poziție (regresie probabilistică)
        self.position_history = []
        self.position_timer = 0
        
    def update(self, keys):
        # Controlul WASD
        if keys[pygame.K_w] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y < SCREEN_HEIGHT - self.visual_size:
            self.y += self.speed
        if keys[pygame.K_a] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < SCREEN_WIDTH - self.visual_size:
            self.x += self.speed
            
        # Actualizează istoricul poziției pentru regresie probabilistică
        self.position_timer += 1
        if self.position_timer >= 30:  # La fiecare jumătate de secundă
            self.position_history.append(self.x + self.visual_size // 2)
            if len(self.position_history) > 10:  # Păstrează ultimele 10 poziții
                self.position_history.pop(0)
            self.position_timer = 0
            
        # Actualizează power-up-uri
        if self.shield_active:
            self.shield_timer -= 1
            self.flash_timer += 1
            if self.shield_timer <= 0:
                self.shield_active = False
                
        if self.invincible:
            self.invincible_timer -= 1
            self.flash_timer += 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def draw(self, screen):
        # Flash effect când e invincibil sau cu scut
        if (self.invincible or self.shield_active) and (self.flash_timer // 3) % 2 == 0:
            return
            
        # Alege culoarea bazată pe starea power-up-ului
        if self.shield_active:
            color = BLUE
        else:
            color = WHITE
            
        pygame.draw.rect(screen, color, (self.x, self.y, self.visual_size, self.visual_size))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.visual_size, self.visual_size), 2)
    
    def get_rect(self):
        # Folosește dimensiunea redusă pentru coliziuni
        offset = (self.visual_size - self.size) // 2
        return pygame.Rect(self.x + offset, self.y + offset, self.size, self.size)
        
    def activate_shield(self, duration_frames):
        self.shield_active = True
        self.shield_timer = duration_frames
        self.flash_timer = 0
        
    def take_damage(self):
        if not self.invincible and not self.shield_active:
            self.hp -= 1
            self.invincible = True
            self.invincible_timer = 60  # 1 secundă la 60 FPS
            self.flash_timer = 0
            return True
        return False
    
    def get_position_weights(self):
        """Returnează ponderile pentru regresie probabilistică"""
        if len(self.position_history) < 3:
            return {}
            
        # Calculează frecvența poziției jucătorului în segmente
        segments = {}
        for pos in self.position_history:
            segment = int(pos // (SCREEN_WIDTH // 8))  # Împarte ecranul în 8 segmente
            segment = max(0, min(7, segment))
            segments[segment] = segments.get(segment, 0) + 1
            
        # Convertește în probabilități (zonele frecventate = probabilitate mai mare)
        weights = {}
        total = sum(segments.values())
        for segment, count in segments.items():
            weights[segment] = count / total
            
        return weights

class ProbabilisticGenerator:
    def __init__(self):
        self.spawn_timer = 0
        self.next_spawn_time = random.randint(500, 1500)  # 0.5-1.5 secunde
        
    def update(self, dt, player):
        self.spawn_timer += dt
        
    def should_spawn_block(self):
        if self.spawn_timer >= self.next_spawn_time:
            self.spawn_timer = 0
            self.next_spawn_time = random.randint(500, 1500)
            return True
        return False
        
    def get_spawn_positions(self, player, grid_manager, current_blocks_count):
        """Generează poziții bazate pe regresie probabilistică și grid management"""
        positions = []
        
        # Verifică câte blocuri mai putem spawna
        max_new_blocks = MAX_SIMULTANEOUS_BLOCKS - current_blocks_count
        if max_new_blocks <= 0:
            return positions
        
        # Obține coloanele libere
        free_columns = grid_manager.get_free_columns()
        if not free_columns:
            return positions
        
        # Obține ponderile poziției jucătorului
        position_weights = player.get_position_weights()
        
        # Determină numărul de blocuri (1-3, dar limitat de spațiul disponibil)
        num_blocks = min(random.randint(1, 3), len(free_columns), max_new_blocks)
        
        # Pentru power-ups, prioritizează zone sigure (opus jucătorului)
        player_center = player.x + player.visual_size // 2
        player_is_left = player_center < SCREEN_WIDTH // 2
        
        for i in range(num_blocks):
            # 5% șansă să fie power-up (redus de la 10%)
            is_powerup = random.random() < 0.05
            
            if is_powerup:
                # Power-up-uri spawn în zone sigure
                if player_is_left:
                    # Jucătorul e în stânga, prioritizează dreapta
                    safe_columns = [col for col in free_columns if col >= GRID_COLUMNS // 2]
                else:
                    # Jucătorul e în dreapta, prioritizează stânga
                    safe_columns = [col for col in free_columns if col < GRID_COLUMNS // 2]
                
                if safe_columns:
                    chosen_column = random.choice(safe_columns)
                else:
                    chosen_column = random.choice(free_columns)
            else:
                # Blocuri normale cu regresie probabilistică
                if position_weights and random.random() < 0.3:  # 30% șansă să folosim regresie
                    # Mapează segmentele la coloane
                    segments = list(position_weights.keys())
                    weights = list(position_weights.values())
                    
                    # Mărește probabilitatea pentru segmentele frecventate
                    enhanced_weights = [w * 1.5 for w in weights]
                    total_weight = sum(enhanced_weights)
                    enhanced_weights = [w / total_weight for w in enhanced_weights]
                    
                    chosen_segment = random.choices(segments, weights=enhanced_weights)[0]
                    # Convertește segmentul la coloane
                    cols_per_segment = GRID_COLUMNS // 8
                    segment_columns = [col for col in free_columns 
                                     if chosen_segment * cols_per_segment <= col < (chosen_segment + 1) * cols_per_segment]
                    
                    if segment_columns:
                        chosen_column = random.choice(segment_columns)
                    else:
                        chosen_column = random.choice(free_columns)
                else:
                    # Poziție complet aleatorie
                    chosen_column = random.choice(free_columns)
            
            x = chosen_column * COLUMN_WIDTH + random.randint(0, COLUMN_WIDTH - BLOCK_SIZE)
            x = max(0, min(x, SCREEN_WIDTH - BLOCK_SIZE))
            positions.append((x, is_powerup))
            
            # Elimină coloana din lista de coloane libere pentru această sesiune de spawn
            free_columns.remove(chosen_column)
            if not free_columns:
                break
            
        return positions

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Evită Blocurile - Joc Avansat")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.state = MENU
        self.reset_game()
        
        # Pentru efectul de puls roșu
        self.screen_flash_timer = 0
        
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.blocks_avoided = 0
        self.blocks = []
        self.particles = []
        self.powerups = []
        self.generator = ProbabilisticGenerator()
        self.grid_manager = GridManager()
        
        self.score = 0
        self.base_score = 0  # Scorul de bază (fără multiplicatori)
        self.start_time = pygame.time.get_ticks()
        self.current_speed = INITIAL_BLOCK_SPEED
        self.speed_increase_timer = 0
        
        # Power-up timers
        self.slow_time_active = False
        self.slow_time_timer = 0
        self.double_points_active = False
        self.double_points_timer = 0
        
        self.screen_flash_timer = 0
        
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
        pass

    def update_game(self):
        keys = pygame.key.get_pressed()
        dt = self.clock.get_time()
        
        # Actualizează personajul
        self.player.update(keys)
        
        # Actualizează flash-ul ecranului
        if self.screen_flash_timer > 0:
            self.screen_flash_timer -= 1
        
        # Actualizează timer-ul de viteză
        self.speed_increase_timer += dt
        if self.speed_increase_timer >= 30000:
            self.current_speed += 1
            self.speed_increase_timer = 0
        
        # Actualizează power-up timers
        if self.slow_time_active:
            self.slow_time_timer -= 1
            if self.slow_time_timer <= 0:
                self.slow_time_active = False
                
        if self.double_points_active:
            self.double_points_timer -= 1
            if self.double_points_timer <= 0:
                self.double_points_active = False
        
        # Actualizează generatorul probabilistic
        self.generator.update(dt, self.player)
        
        # Actualizează grid manager-ul
        all_blocks = self.blocks + self.powerups
        self.grid_manager.update_from_blocks(all_blocks)
        
        # Spawnează blocuri și power-ups
        if self.generator.should_spawn_block():
            current_blocks_count = len(self.blocks) + len(self.powerups)
            positions = self.generator.get_spawn_positions(self.player, self.grid_manager, current_blocks_count)
            
            for x, is_powerup in positions:
                if is_powerup:
                    powerup_type = random.randint(0, 2)
                    speed = self.current_speed * 0.5 if self.slow_time_active else self.current_speed
                    self.powerups.append(PowerUp(x, -24, powerup_type, speed))
                else:
                    speed = self.current_speed * 0.5 if self.slow_time_active else self.current_speed
                    self.blocks.append(Block(x, -BLOCK_SIZE, speed))
        
        # Actualizează blocurile și verifică dacă au ieșit complet de pe ecran
        for block in self.blocks[:]:
            # Aplică slow time effect
            if self.slow_time_active:
                block.speed = self.current_speed * 0.5
            else:
                block.speed = self.current_speed
                
            block.update()
            
            # Verifică dacă blocul a trecut COMPLET de marginea de jos
            if block.is_completely_off_screen():
                self.blocks.remove(block)
                # PUNCTAJ: Adaugă puncte doar când blocul trece complet de ecran
                points_to_add = 2 if self.double_points_active else 1
                self.blocks_avoided += points_to_add
                print(f"Block avoided! Points added: {points_to_add}, Total blocks avoided: {self.blocks_avoided}")
                
        # Actualizează power-ups
        for powerup in self.powerups[:]:
            # Aplică slow time effect și pentru power-ups
            if self.slow_time_active:
                powerup.speed = self.current_speed * 0.5
            else:
                powerup.speed = self.current_speed
                
            powerup.update()
            # Power-up-urile nu dau puncte când trec de ecran
            if powerup.is_completely_off_screen():
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
                if powerup.type == POWERUP_SHIELD:
                    self.player.activate_shield(180)  # 3 secunde
                elif powerup.type == POWERUP_SLOW:
                    self.slow_time_active = True
                    self.slow_time_timer = 300  # 5 secunde
                elif powerup.type == POWERUP_DOUBLE:
                    self.double_points_active = True
                    self.double_points_timer = 600  # 10 secunde
                    
                self.powerups.remove(powerup)
                break
        
        # Verifică coliziunile cu blocurile
        for block in self.blocks[:]:
            if player_rect.colliderect(block.get_rect()):
                if self.player.take_damage():
                    # Efectul de flash roșu
                    self.screen_flash_timer = 18  # 0.3 secunde la 60 FPS
                    
                    # Creează particule de impact
                    for _ in range(12):
                        self.particles.append(Particle(self.player.x + self.player.visual_size//2, 
                                                    self.player.y + self.player.visual_size//2))
                    self.blocks.remove(block)
                    
                    # Verifică game over
                    if self.player.hp <= 0:
                        self.state = GAME_OVER
                    break
                    
        # Calculează scorul
        current_time = (pygame.time.get_ticks() - self.start_time) // 1000
        base_time_score = current_time
        total_score = base_time_score + self.blocks_avoided

        if self.double_points_active:
            # Aplică bonusul doar la punctele din timp, nu la blocurile evitate
            # (blocurile evitate deja au bonusul aplicat când sunt evitate)
            self.score = (base_time_score * 2) + self.blocks_avoided
        else:
            self.score = total_score

    def update_game_over(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
    
    def draw_hearts(self):
        """Desenează inimile pentru HP cu efect de dispariție progresivă"""
        heart_size = 20
        for i in range(self.player.max_hp):
            x = 10 + i * (heart_size + 5)
            y = 10
            
            if i < self.player.hp:
                # Inimă plină
                color = RED
                alpha = 255
            else:
                # Inimă pierdută - efect de dispariție
                color = DARK_GRAY
                # Calculează alpha bazat pe timpul de la pierderea inimii
                fade_factor = max(0, (self.player.max_hp - i - 1) * 0.3)
                alpha = max(50, int(255 * fade_factor))
                color = (alpha//4, alpha//4, alpha//4)
                
            # Desenează inima ca două cercuri și un triunghi
            pygame.draw.circle(self.screen, color, (x + 6, y + 6), 6)
            pygame.draw.circle(self.screen, color, (x + 14, y + 6), 6)
            points = [(x + 2, y + 8), (x + 10, y + 18), (x + 18, y + 8)]
            pygame.draw.polygon(self.screen, color, points)
            
            # Contur negru doar pentru inimile pline
            if i < self.player.hp:
                pygame.draw.circle(self.screen, BLACK, (x + 6, y + 6), 6, 2)
                pygame.draw.circle(self.screen, BLACK, (x + 14, y + 6), 6, 2)
                pygame.draw.polygon(self.screen, BLACK, points, 2)
        
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title_text = self.font_large.render("EVITĂ BLOCURILE", True, WHITE)
        subtitle_text = self.font_medium.render("Versiunea Avansată", True, GRAY)
        start_text = self.font_medium.render("Apasă SPACE pentru a începe", True, WHITE)
        controls_text = self.font_small.render("Controluri: WASD", True, GRAY)
        powerups_text = self.font_small.render("Power-ups: Scut, Încetinire, Puncte Duble", True, GRAY)
        quit_text = self.font_small.render("ESC pentru ieșire", True, GRAY)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        powerups_rect = powerups_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(start_text, start_rect)
        self.screen.blit(controls_text, controls_rect)
        self.screen.blit(powerups_text, powerups_rect)
        self.screen.blit(quit_text, quit_rect)
        
    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Efect de flash roșu când jucătorul e lovit
        if self.screen_flash_timer > 0:
            flash_intensity = int((self.screen_flash_timer / 18.0) * 50)
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill((flash_intensity, 0, 0))
            flash_surface.set_alpha(flash_intensity)
            self.screen.blit(flash_surface, (0, 0))
        
        # Desenează toate obiectele jocului
        self.player.draw(self.screen)
        for block in self.blocks:
            block.draw(self.screen)
        for powerup in self.powerups:
            powerup.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
            
        # Desenează inimile
        self.draw_hearts()
            
        # UI
        score_text = self.font_medium.render(f"Scor: {self.score}", True, WHITE)
        blocks_avoided_text = self.font_small.render(f"Blocuri evitate: {self.blocks_avoided}", True, WHITE)
        speed_text = self.font_small.render(f"Viteză: {self.current_speed}", True, WHITE)
        blocks_text = self.font_small.render(f"Blocuri: {len(self.blocks) + len(self.powerups)}/{MAX_SIMULTANEOUS_BLOCKS}", True, WHITE)
        
        self.screen.blit(score_text, (10, 50))
        self.screen.blit(blocks_avoided_text, (10, 80))
        self.screen.blit(speed_text, (10, 110))
        self.screen.blit(blocks_text, (10, 140))
        
        # Afișează power-up-uri active
        y_offset = 10
        if self.player.shield_active:
            shield_time = self.player.shield_timer / 60.0
            shield_text = self.font_small.render(f"Scut: {shield_time:.1f}s", True, BLUE)
            self.screen.blit(shield_text, (SCREEN_WIDTH - 150, y_offset))
            y_offset += 25
            
        if self.slow_time_active:
            slow_time = self.slow_time_timer / 60.0
            slow_text = self.font_small.render(f"Încetinire: {slow_time:.1f}s", True, YELLOW)
            self.screen.blit(slow_text, (SCREEN_WIDTH - 150, y_offset))
            y_offset += 25
            
        if self.double_points_active:
            double_time = self.double_points_timer / 60.0
            double_text = self.font_small.render(f"Puncte x2: {double_time:.1f}s", True, GOLD)
            self.screen.blit(double_text, (SCREEN_WIDTH - 150, y_offset))
        
    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        # Desenează particulele de explozie în continuare
        for particle in self.particles:
            particle.draw(self.screen)
            
        # Overlay semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        # Text principal
        game_over_text = self.font_large.render("GAME OVER", True, WHITE)
        score_text = self.font_medium.render(f"Scor Final: {self.score}", True, WHITE)
        
        # Calculează timpul de supraviețuire
        survival_time = self.score
        minutes = survival_time // 60
        seconds = survival_time % 60
        time_text = self.font_medium.render(f"Timp Supraviețuire: {minutes:02d}:{seconds:02d}", True, GRAY)
        
        # Instrucțiuni
        restart_text = self.font_medium.render("Apasă R pentru Restart", True, GREEN)
        menu_text = self.font_medium.render("Apasă SPACE pentru Meniu", True, WHITE)
        quit_text = self.font_small.render("ESC pentru Ieșire", True, GRAY)
        
        # Poziționare text
        y_start = SCREEN_HEIGHT // 2 - 120
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, y_start))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, y_start + 60))
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, y_start + 100))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, y_start + 160))
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, y_start + 200))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, y_start + 240))
        
        # Desenează toate textele
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(time_text, time_rect)
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(menu_text, menu_rect)
        self.screen.blit(quit_text, quit_rect)
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            if self.state == MENU:
                self.update_menu()
                self.draw_menu()
            elif self.state == GAME:
                self.update_game()
                self.draw_game()
            elif self.state == GAME_OVER:
                self.update_game_over()
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()