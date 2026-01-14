import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = 8
        self.color = CYAN
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.shoot_delay = 10
        self.power_level = 1
        self.power_time = 0
        self.score = 0
        self.lives = 3
        self.invincible = 0
        self.weapon_type = "normal"
        self.special_ammo = 0
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
            
    def shoot(self, bullets):
        if self.shoot_cooldown <= 0:
            if self.weapon_type == "normal":
                bullets.append(Bullet(self.x + self.width//2 - 2, self.y, -10, GREEN))
                if self.power_level >= 2:
                    bullets.append(Bullet(self.x + 10, self.y, -10, GREEN))
                    bullets.append(Bullet(self.x + self.width - 15, self.y, -10, GREEN))
                if self.power_level >= 3:
                    bullets.append(Bullet(self.x + 5, self.y + 10, -10, GREEN, angle=-5))
                    bullets.append(Bullet(self.x + self.width - 10, self.y + 10, -10, GREEN, angle=5))
            elif self.weapon_type == "laser":
                bullets.append(LaserBeam(self.x + self.width//2 - 2, self.y))
                self.special_ammo -= 1
                if self.special_ammo <= 0:
                    self.weapon_type = "normal"
                    
            self.shoot_cooldown = self.shoot_delay
            
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.power_time > 0:
            self.power_time -= 1
            if self.power_time == 0:
                self.power_level = max(1, self.power_level - 1)
        if self.invincible > 0:
            self.invincible -= 1
            
    def draw(self, screen):
        # Draw ship with invincibility blink
        if self.invincible <= 0 or self.invincible % 8 < 4:
            # Main body
            pygame.draw.polygon(screen, self.color, [
                (self.x + self.width//2, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ])
            # Cockpit
            pygame.draw.rect(screen, BLUE, 
                            (self.x + self.width//2 - 10, self.y + 10, 20, 15))
            # Engines
            pygame.draw.rect(screen, ORANGE, 
                            (self.x + 10, self.y + self.height - 10, 10, 10))
            pygame.draw.rect(screen, ORANGE, 
                            (self.x + self.width - 20, self.y + self.height - 10, 10, 10))
            
        # Health bar
        bar_width = 100
        bar_height = 10
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x + self.width//2 - bar_width//2, 
                                      self.y - 20, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x + self.width//2 - bar_width//2, 
                                        self.y - 20, bar_width * health_ratio, bar_height))
        
    def take_damage(self, amount):
        if self.invincible <= 0:
            self.health -= amount
            self.invincible = 60  # 1 second invincibility
            return True
        return False

class Bullet:
    def __init__(self, x, y, speed, color, angle=0):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.width = 4
        self.height = 10
        self.angle = angle
        self.damage = 10
        
    def update(self):
        self.y += self.speed
        if self.angle != 0:
            self.x += self.angle
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def is_off_screen(self):
        return self.y < -self.height or self.y > SCREEN_HEIGHT or self.x < 0 or self.x > SCREEN_WIDTH

class LaserBeam:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = SCREEN_HEIGHT
        self.damage = 5
        self.lifetime = 10
        
    def update(self):
        self.lifetime -= 1
        
    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.rect(screen, YELLOW, (self.x, 0, self.width, self.y))
            
    def is_active(self):
        return self.lifetime > 0

class Enemy:
    def __init__(self, enemy_type="basic"):
        self.type = enemy_type
        self.setup_enemy()
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = random.randint(-100, -40)
        self.shoot_timer = random.randint(30, 180)
        self.health = self.max_health
        self.hit_timer = 0
        
    def setup_enemy(self):
        if self.type == "basic":
            self.width = 40
            self.height = 40
            self.speed = random.uniform(1.0, 3.0)
            self.color = RED
            self.max_health = 20
            self.score_value = 10
            self.shoot_delay = 120
        elif self.type == "fast":
            self.width = 30
            self.height = 30
            self.speed = random.uniform(3.0, 5.0)
            self.color = PURPLE
            self.max_health = 15
            self.score_value = 15
            self.shoot_delay = 90
        elif self.type == "tank":
            self.width = 60
            self.height = 60
            self.speed = random.uniform(0.5, 1.5)
            self.color = ORANGE
            self.max_health = 60
            self.score_value = 30
            self.shoot_delay = 60
        elif self.type == "boss":
            self.width = 120
            self.height = 120
            self.speed = 1.0
            self.color = (200, 0, 0)
            self.max_health = 300
            self.score_value = 500
            self.shoot_delay = 30
            self.pattern_timer = 0
            
    def update(self):
        self.y += self.speed
        self.shoot_timer -= 1
        
        if self.type == "boss":
            self.x += math.sin(self.pattern_timer * 0.05) * 2
            self.pattern_timer += 1
            
        if self.hit_timer > 0:
            self.hit_timer -= 1
            
    def draw(self, screen):
        color = self.color
        if self.hit_timer > 0:
            color = WHITE
            
        if self.type == "boss":
            # Draw boss with more detail
            pygame.draw.ellipse(screen, color, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, YELLOW, (int(self.x + self.width//2), 
                                              int(self.y + self.height//2)), 20)
            pygame.draw.circle(screen, BLACK, (int(self.x + self.width//2), 
                                             int(self.y + self.height//2)), 10)
            # Health bar for boss
            bar_width = self.width
            bar_height = 8
            health_ratio = self.health / self.max_health
            pygame.draw.rect(screen, RED, (self.x, self.y - 15, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 15, bar_width * health_ratio, bar_height))
        else:
            pygame.draw.polygon(screen, color, [
                (self.x + self.width//2, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ])
            # Enemy cockpit
            pygame.draw.circle(screen, BLACK, 
                             (int(self.x + self.width//2), int(self.y + self.height//3)), 
                             self.width//6)
            
    def shoot(self, enemy_bullets):
        if self.shoot_timer <= 0:
            if self.type == "boss":
                # Boss shooting pattern
                for angle in range(0, 360, 30):
                    rad = math.radians(angle + self.pattern_timer * 5)
                    enemy_bullets.append(
                        EnemyBullet(self.x + self.width//2, self.y + self.height, 
                                   math.sin(rad) * 3, math.cos(rad) * 3, "boss")
                    )
                self.shoot_timer = self.shoot_delay
            else:
                enemy_bullets.append(
                    EnemyBullet(self.x + self.width//2, self.y + self.height, 
                               0, 5, self.type)
                )
                self.shoot_timer = self.shoot_delay + random.randint(-30, 30)
                
    def take_damage(self, amount):
        self.health -= amount
        self.hit_timer = 5
        return self.health <= 0
        
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class EnemyBullet:
    def __init__(self, x, y, dx, dy, bullet_type):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.type = bullet_type
        self.setup_bullet()
        
    def setup_bullet(self):
        if self.type == "boss":
            self.width = 8
            self.height = 8
            self.color = PURPLE
            self.damage = 20
        else:
            self.width = 6
            self.height = 12
            self.color = RED
            self.damage = 10
            
    def update(self):
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def is_off_screen(self):
        return (self.y > SCREEN_HEIGHT or self.y < 0 or 
                self.x < 0 or self.x > SCREEN_WIDTH)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.width = 30
        self.height = 30
        self.speed = 2
        self.setup_powerup()
        
    def setup_powerup(self):
        if self.type == "health":
            self.color = GREEN
        elif self.type == "weapon":
            self.color = YELLOW
        elif self.type == "shield":
            self.color = BLUE
        elif self.type == "laser":
            self.color = ORANGE
            
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        if self.type == "health":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 15)
            pygame.draw.polygon(screen, WHITE, [
                (self.x, self.y - 8),
                (self.x - 6, self.y + 4),
                (self.x + 6, self.y + 4)
            ])
        elif self.type == "weapon":
            pygame.draw.rect(screen, self.color, 
                            (self.x - 10, self.y - 10, 20, 20))
            pygame.draw.rect(screen, BLACK, 
                            (self.x - 5, self.y - 15, 10, 20))
        elif self.type == "shield":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 15, 3)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10, 3)
        elif self.type == "laser":
            pygame.draw.rect(screen, self.color, 
                            (self.x - 12, self.y - 3, 24, 6))
            pygame.draw.rect(screen, self.color, 
                            (self.x - 3, self.y - 12, 6, 24))
            
    def apply(self, player):
        if self.type == "health":
            player.health = min(player.max_health, player.health + 30)
        elif self.type == "weapon":
            player.power_level = min(3, player.power_level + 1)
            player.power_time = 600  # 10 seconds
        elif self.type == "shield":
            player.invincible = 180  # 3 seconds
        elif self.type == "laser":
            player.weapon_type = "laser"
            player.special_ammo = 50
            
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)
        
    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
            
    def is_dead(self):
        return self.lifetime <= 0

class Starfield:
    def __init__(self):
        self.stars = []
        for _ in range(200):
            self.stars.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.uniform(0.1, 0.5)
            ])
            
    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)
                
    def draw(self, screen):
        for x, y, speed in self.stars:
            brightness = int(speed * 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (int(x), int(y)), 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Galactic Defender")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.wave = 1
        self.enemies_to_spawn = 5
        self.enemies_spawned = 0
        self.wave_timer = 0
        self.boss_wave = False
        
        # Game objects
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.powerups = []
        self.particles = []
        self.starfield = Starfield()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.__init__()  # Restart game
                elif event.key == pygame.K_z:  # Rapid fire hold
                    self.player.shoot(self.bullets)
                    
    def spawn_enemies(self):
        if self.wave_timer <= 0 and self.enemies_spawned < self.enemies_to_spawn:
            if self.wave % 5 == 0:  # Boss every 5 waves
                if not self.boss_wave:
                    self.enemies.append(Enemy("boss"))
                    self.boss_wave = True
                    self.enemies_spawned = self.enemies_to_spawn
            else:
                enemy_types = ["basic", "fast", "tank"]
                weights = [0.5, 0.3, 0.2]
                enemy_type = random.choices(enemy_types, weights=weights)[0]
                self.enemies.append(Enemy(enemy_type))
                self.enemies_spawned += 1
                self.wave_timer = 30  # Small delay between spawns
                
    def spawn_powerup(self, x, y):
        types = ["health", "weapon", "shield", "laser"]
        weights = [0.4, 0.3, 0.2, 0.1]
        power_type = random.choices(types, weights=weights)[0]
        self.powerups.append(PowerUp(x, y, power_type))
        
    def check_collisions(self):
        # Player bullets vs enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (bullet.x < enemy.x + enemy.width and
                    bullet.x + bullet.width > enemy.x and
                    bullet.y < enemy.y + enemy.height and
                    bullet.y + bullet.height > enemy.y):
                    
                    if enemy.take_damage(bullet.damage):
                        # Enemy destroyed
                        self.player.score += enemy.score_value
                        self.enemies.remove(enemy)
                        
                        # Create explosion particles
                        for _ in range(20):
                            self.particles.append(Particle(
                                enemy.x + enemy.width//2,
                                enemy.y + enemy.height//2,
                                enemy.color
                            ))
                        
                        # Chance to spawn powerup
                        if random.random() < 0.2:
                            self.spawn_powerup(
                                enemy.x + enemy.width//2,
                                enemy.y + enemy.height//2
                            )
                    
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
                    
        # Enemy bullets vs player
        for bullet in self.enemy_bullets[:]:
            if (bullet.x < self.player.x + self.player.width and
                bullet.x + bullet.width > self.player.x and
                bullet.y < self.player.y + self.player.height and
                bullet.y + bullet.height > self.player.y):
                
                if self.player.take_damage(bullet.damage):
                    # Create hit particles
                    for _ in range(10):
                        self.particles.append(Particle(
                            self.player.x + self.player.width//2,
                            self.player.y + self.player.height//2,
                            RED
                        ))
                
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
                    
        # Laser vs enemies
        for bullet in self.bullets:
            if isinstance(bullet, LaserBeam):
                for enemy in self.enemies[:]:
                    if (bullet.x < enemy.x + enemy.width and
                        bullet.x + bullet.width > enemy.x):
                        
                        if enemy.take_damage(bullet.damage):
                            # Enemy destroyed
                            self.player.score += enemy.score_value
                            self.enemies.remove(enemy)
                            
                            for _ in range(20):
                                self.particles.append(Particle(
                                    enemy.x + enemy.width//2,
                                    enemy.y + enemy.height//2,
                                    enemy.color
                                ))
                            
                            if random.random() < 0.2:
                                self.spawn_powerup(
                                    enemy.x + enemy.width//2,
                                    enemy.y + enemy.height//2
                                )
        
        # Player vs enemies
        for enemy in self.enemies[:]:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                
                if self.player.take_damage(30):
                    for _ in range(15):
                        self.particles.append(Particle(
                            self.player.x + self.player.width//2,
                            self.player.y + self.player.height//2,
                            RED
                        ))
                
                if enemy.take_damage(50):
                    self.player.score += enemy.score_value
                    self.enemies.remove(enemy)
                    
                    for _ in range(20):
                        self.particles.append(Particle(
                            enemy.x + enemy.width//2,
                            enemy.y + enemy.height//2,
                            enemy.color
                        ))
                        
                    if random.random() < 0.2:
                        self.spawn_powerup(
                            enemy.x + enemy.width//2,
                            enemy.y + enemy.height//2
                        )
        
        # Player vs powerups
        for powerup in self.powerups[:]:
            if (self.player.x < powerup.x + powerup.width and
                self.player.x + self.player.width > powerup.x and
                self.player.y < powerup.y + powerup.height and
                self.player.y + self.player.height > powerup.y):
                
                powerup.apply(self.player)
                self.powerups.remove(powerup)
                
                # Create collect particles
                for _ in range(15):
                    self.particles.append(Particle(
                        powerup.x, powerup.y, powerup.color
                    ))
    
    def update(self):
        if not self.game_over:
            # Update player
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.update()
            
            # Auto-shoot when holding space
            if keys[pygame.K_SPACE]:
                self.player.shoot(self.bullets)
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update()
                if hasattr(bullet, 'is_off_screen') and bullet.is_off_screen():
                    self.bullets.remove(bullet)
                elif hasattr(bullet, 'is_active') and not bullet.is_active():
                    self.bullets.remove(bullet)
            
            # Update enemy bullets
            for bullet in self.enemy_bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    self.enemy_bullets.remove(bullet)
            
            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update()
                enemy.shoot(self.enemy_bullets)
                if enemy.is_off_screen():
                    self.enemies.remove(enemy)
            
            # Update powerups
            for powerup in self.powerups[:]:
                powerup.update()
                if powerup.is_off_screen():
                    self.powerups.remove(powerup)
            
            # Update particles
            for particle in self.particles[:]:
                particle.update()
                if particle.is_dead():
                    self.particles.remove(particle)
            
            # Update starfield
            self.starfield.update()
            
            # Spawn logic
            if self.wave_timer > 0:
                self.wave_timer -= 1
            
            self.spawn_enemies()
            
            # Check if wave is complete
            if (len(self.enemies) == 0 and 
                self.enemies_spawned >= self.enemies_to_spawn):
                if self.wave % 5 == 0 and self.boss_wave:
                    self.boss_wave = False
                    self.player.score += 1000  # Bonus for beating boss
                
                self.wave += 1
                self.enemies_to_spawn = min(20, 5 + self.wave * 2)
                self.enemies_spawned = 0
                self.wave_timer = 180  # 3 second break between waves
            
            # Check collisions
            self.check_collisions()
            
            # Check game over
            if self.player.health <= 0:
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True
                else:
                    self.player.health = self.player.max_health
                    self.player.invincible = 180  # 3 seconds respawn invincibility
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw starfield
        self.starfield.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Score
        score_text = self.font_medium.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Wave
        wave_text = self.font_medium.render(f"Wave: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (10, 50))
        
        # Lives
        lives_text = self.font_medium.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        
        # Weapon status
        if self.player.weapon_type == "normal":
            weapon_text = self.font_small.render(f"Weapon: Level {self.player.power_level}", True, YELLOW)
        else:
            weapon_text = self.font_small.render(f"Weapon: LASER ({self.player.special_ammo})", True, ORANGE)
        self.screen.blit(weapon_text, (SCREEN_WIDTH - 150, 50))
        
        # Powerup timer
        if self.player.power_time > 0:
            timer_text = self.font_small.render(f"Power: {self.player.power_time//60}s", True, GREEN)
            self.screen.blit(timer_text, (SCREEN_WIDTH - 150, 80))
        
        # Controls help
        controls = [
            "CONTROLS:",
            "Arrow Keys - Move",
            "Space - Shoot (Hold)",
            "Z - Single Shot"
        ]
        
        for i, line in enumerate(controls):
            control_text = self.font_small.render(line, True, (150, 150, 150))
            self.screen.blit(control_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 120 + i * 25))
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                         SCREEN_HEIGHT//2 - 100))
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, 
                        (SCREEN_WIDTH//2 - score_text.get_width()//2, 
                         SCREEN_HEIGHT//2 - 30))
        
        # Wave reached
        wave_text = self.font_medium.render(f"Waves Survived: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, 
                        (SCREEN_WIDTH//2 - wave_text.get_width()//2, 
                         SCREEN_HEIGHT//2 + 10))
        
        # Restart instructions
        restart_text = self.font_medium.render("Press SPACE to restart or ESC to quit", True, GREEN)
        self.screen.blit(restart_text, 
                        (SCREEN_WIDTH//2 - restart_text.get_width()//2, 
                         SCREEN_HEIGHT//2 + 80))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()