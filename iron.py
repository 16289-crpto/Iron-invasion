import pygame
import random

# Initialiseer Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BASE_WIDTH = 100
BASE_HEIGHT = 20
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
PLAYER_UNIT_WIDTH = 30
PLAYER_UNIT_HEIGHT = 30
FPS = 60

# Kleuren
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Basis Klasse
class Base:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BASE_WIDTH, BASE_HEIGHT)
        self.health = 100

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN if self.health > 0 else RED, self.rect)

# Vijand Klasse
class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH), 0, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.speed = random.randint(1, 3)
        self.health = 10
        self.coins = random.randint(1, 3)  # Munten die de vijand laat vallen

    def move(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

# Speler Eenheid Klasse
class PlayerUnit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_UNIT_WIDTH, PLAYER_UNIT_HEIGHT)
        self.health = 10
        self.attack_power = 1

    def attack(self, enemies):
        coins_dropped = 0
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.health -= self.attack_power
                if enemy.health <= 0:
                    coins_dropped += enemy.coins  # Voeg munten toe als de vijand is verslagen
                    enemies.remove(enemy)  # Verwijder de verslagen vijand
        return coins_dropped

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect)

# Game Manager Klasse
class GameManager:
    def __init__(self):
        self.defending_base = Base(SCREEN_WIDTH // 2 - BASE_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.enemies = []
        self.player_units = []
        self.coins = 0
        self.wave_number = 0
        self.spawn_timer = 0

    def spawn_enemies(self):
        if self.spawn_timer <= 0:
            self.wave_number += 1
            for _ in range(self.wave_number):
                self.enemies.append(Enemy())
            self.spawn_timer = 60  # Reset timer (60 frames = 1 seconde)

    def update(self):
        self.spawn_enemies()
        for enemy in self.enemies:
            enemy.move()
            if enemy.rect.colliderect(self.defending_base.rect):
                self.defending_base.health -= 1
                self.enemies.remove(enemy)

        # Controleer aanvallen van speler eenheden
        for unit in self.player_units:
            coins_dropped = unit.attack(self.enemies)
            self.coins += coins_dropped

        self.spawn_timer -= 1

    def draw(self, screen):
        self.defending_base.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        for unit in self.player_units:
            unit.draw(screen)

    def spawn_player_unit(self, x, y):
        self.player_units.append(PlayerUnit(x, y))

# Hoofd Game Loop
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Base Assault: Infinite Waves")
    clock = pygame.time.Clock()
    game_manager = GameManager()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Druk op spatie om een speler eenheid te spawnen
                    game_manager.spawn