import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PATH_TOP = SCREEN_HEIGHT // 4
PATH_BOTTOM = 3 * SCREEN_HEIGHT // 4
FPS = 60
TANK_COST = 50
TANK_DAMAGE = 15
ENEMY_DAMAGE = 10
RESOURCE_GAIN = 20
TANK_HEALTH = 200
ENEMY_HEALTH = 100
FONT = pygame.font.Font(None, 36)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tanks vs Enemies")
clock = pygame.time.Clock()

# Classes
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = TANK_HEALTH
        self.damage = TANK_DAMAGE
        self.speed = 2
        self.target = None

    def find_target(self, enemies):
        if enemies:
            self.target = min(enemies, key=lambda enemy: math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery))
        else:
            self.target = None

    def move_and_attack(self):
        if self.target:
            # Move towards target
            dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                dx, dy = dx / distance, dy / distance
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            # Attack if close enough
            if distance < 20:
                self.target.health -= self.damage
                if self.target.health <= 0:
                    self.target.kill()
                    return RESOURCE_GAIN
        return 0

    def draw_health_bar(self, screen):
        # Draw health bar above the tank
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / TANK_HEALTH
        bar_color = GREEN if health_ratio > 0.5 else RED
        pygame.draw.rect(screen, GRAY, (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (self.rect.centerx - bar_width // 2, self.rect.top - 10, int(bar_width * health_ratio), bar_height))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = ENEMY_HEALTH
        self.speed = speed
        self.target = None

    def find_target(self, tanks):
        if tanks:
            self.target = min(tanks, key=lambda tank: math.hypot(self.rect.centerx - tank.rect.centerx, self.rect.centery - tank.rect.centery))
        else:
            self.target = None

    def move_and_attack(self):
        if self.target:
            # Move towards target
            dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                dx, dy = dx / distance, dy / distance
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            # Attack if close enough
            if distance < 20:
                self.target.health -= ENEMY_DAMAGE
                if self.target.health <= 0:
                    self.target.kill()
        else:
            # Move straight within path
            self.rect.x += self.speed
            if self.rect.y < PATH_TOP:
                self.rect.y = PATH_TOP
            elif self.rect.y > PATH_BOTTOM:
                self.rect.y = PATH_BOTTOM

    def draw_health_bar(self, screen):
        # Draw health bar above the enemy
        bar_width = 30
        bar_height = 5
        health_ratio = self.health / ENEMY_HEALTH
        bar_color = GREEN if health_ratio > 0.5 else RED
        pygame.draw.rect(screen, GRAY, (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (self.rect.centerx - bar_width // 2, self.rect.top - 10, int(bar_width * health_ratio), bar_height))

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.text = text
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Game:
    def __init__(self):
        self.tanks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.resources = 100
        self.spawn_timer = 0
        self.wave = 1

        # Create button
        self.tank_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 40, "Place Tank", self.place_tank)

    def spawn_enemy(self):
        if pygame.time.get_ticks() - self.spawn_timer > 2000:  # Spawn every 2 seconds
            self.spawn_timer = pygame.time.get_ticks()
            y = random.randint(PATH_TOP, PATH_BOTTOM)
            enemy = Enemy(0, y, random.randint(2, 4))
            self.enemies.add(enemy)

    def place_tank(self):
        if self.resources >= TANK_COST:
            x = random.randint(SCREEN_WIDTH - 100, SCREEN_WIDTH - 40)
            y = random.randint(PATH_TOP, PATH_BOTTOM)
            tank = Tank(x, y)
            self.tanks.add(tank)
            self.resources -= TANK_COST

    def handle_tank_actions(self):
        resource_gain = 0
        for tank in self.tanks:
            tank.find_target(self.enemies)
            resource_gain += tank.move_and_attack()
        self.resources += resource_gain

    def handle_enemy_actions(self):
        for enemy in self.enemies:
            enemy.find_target(self.tanks)
            enemy.move_and_attack()

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.tank_button.is_clicked(mouse_pos):
                self.tank_button.action()

    def draw_ui(self):
        # Resources display
        resources_text = FONT.render(f"Resources: {self.resources}", True, WHITE)
        screen.blit(resources_text, (10, 10))

        # Wave display
        wave_text = FONT.render(f"Wave: {self.wave}", True, WHITE)
        screen.blit(wave_text, (10, 50))

        # Draw button
        self.tank_button.draw(screen)

    def update_wave(self):
        if not self.enemies:
            self.wave += 1
            for _ in range(self.wave * 5):  # Increase enemy count per wave
                y = random.randint(PATH_TOP, PATH_BOTTOM)
                enemy = Enemy(0, y, random.randint(2, 4))
                self.enemies.add(enemy)

    def run(self):
        running = True
        while running:
            screen.fill(BLACK)

            # Draw path
            pygame.draw.rect(screen, GRAY, (0, PATH_TOP, SCREEN_WIDTH, PATH_BOTTOM - PATH_TOP))

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_input(event)

            # Game logic
            self.spawn_enemy()
            self.handle_tank_actions()
            self.handle_enemy_actions()
            self.update_wave()

            # Draw everything
            self.tanks.draw(screen)
            self.enemies.draw(screen)
            for tank in self.tanks:
                tank.draw_health_bar(screen)
            for enemy in self.enemies:
                enemy.draw_health_bar(screen)
            self.draw_ui()

            pygame.display.flip()
            clock.tick(FPS)

# Main game loop
game = Game()
game.run()

pygame.quit()