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
BASE_TANK_DAMAGE = 15
BASE_TANK_HEALTH = 200
ENEMY_DAMAGE = 10
ENEMY_HEALTH = 100
MAX_ESCAPED_ENEMIES = 10
FONT = pygame.font.Font(None, 36)
RESOURCE_GENERATION_INTERVAL = 1000  # 1 second

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Upgrade Variables
upgrade_points = 0
tank_damage_upgrade = 0
tank_health_upgrade = 0

# Game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Iron Fuckin Invasion BABAYYYY")
clock = pygame.time.Clock()

# Classes
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = BASE_TANK_HEALTH + tank_health_upgrade * 50
        self.damage = BASE_TANK_DAMAGE + tank_damage_upgrade * 5
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
                    global upgrade_points
                    upgrade_points += 1  # Earn an upgrade point
                    self.target.kill()

    def draw_health_bar(self, screen):
        bar_width = 40
        bar_height = 5
        max_health = BASE_TANK_HEALTH + tank_health_upgrade * 50
        health_ratio = self.health / max_health
        bar_color = GREEN if health_ratio > 0.5 else RED
        pygame.draw.rect(screen, GRAY, (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (self.rect.centerx - bar_width // 2, self.rect.top - 10, int(bar_width * health_ratio), bar_height))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, health):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health
        self.max_health = health  # Store maximum health for consistent health bar
        self.speed = speed
        self.target = None

    def find_target(self, tanks):
        if tanks:
            self.target = min(tanks, key=lambda tank: math.hypot(self.rect.centerx - tank.rect.centerx, self.rect.centery - tank.rect.centery))
        else:
            self.target = None

    def move_and_attack(self):
        if self.target:
            dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                dx, dy = dx / distance, dy / distance
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            if distance < 20:
                self.target.health -= ENEMY_DAMAGE
                if self.target.health <= 0:
                    self.target.kill()
        else:
            self.rect.x += self.speed
            if self.rect.x > SCREEN_WIDTH:
                self.escaped = True  # Mark enemy as escaped

    def draw_health_bar(self, screen):
        bar_width = 30
        bar_height = 5
        health_ratio = self.health / self.max_health
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
        self.resource_timer = pygame.time.get_ticks()
        self.spawn_timer = 0
        self.wave = 1
        self.escaped_enemies = 0
        self.wave_active = True
        self.enemies_to_spawn = 5  # Number of enemies in the first wave
        self.spawned_enemies = 0  # Track how many enemies have been spawned
        self.enemy_health_multiplier = 1.0
        self.enemy_speed_multiplier = 1.0
        self.tank_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 40, "Place Tank", self.place_tank)

    def generate_resources(self):
        if pygame.time.get_ticks() - self.resource_timer > RESOURCE_GENERATION_INTERVAL:
            self.resource_timer = pygame.time.get_ticks()
            self.resources += 10

    def spawn_enemy(self):
        if self.wave_active and self.spawned_enemies < self.enemies_to_spawn:
            if pygame.time.get_ticks() - self.spawn_timer > 2000:
                self.spawn_timer = pygame.time.get_ticks()
                y = random.randint(PATH_TOP, PATH_BOTTOM)
                speed = random.randint(2, 4) * self.enemy_speed_multiplier
                health = ENEMY_HEALTH * self.enemy_health_multiplier
                enemy = Enemy(0, y, speed, health)
                self.enemies.add(enemy)
                self.spawned_enemies += 1

    def check_wave_end(self):
        if self.spawned_enemies == self.enemies_to_spawn and len(self.enemies) == 0:
            self.wave_active = False
            self.start_new_wave()

    def start_new_wave(self):
        self.wave += 1
        self.enemy_health_multiplier += 0.2
        self.enemy_speed_multiplier += 0.1
        self.enemies_to_spawn += 3  # Increase number of enemies per wave
        self.spawned_enemies = 0
        self.wave_active = True

    def place_tank(self):
        global tank_health_upgrade, tank_damage_upgrade
        if self.resources >= TANK_COST:
            x = random.randint(SCREEN_WIDTH - 100, SCREEN_WIDTH - 40)
            y = random.randint(PATH_TOP, PATH_BOTTOM)
            tank = Tank(x, y)
            self.tanks.add(tank)
            self.resources -= TANK_COST

    def handle_tank_actions(self):
        for tank in self.tanks:
            tank.find_target(self.enemies)
            tank.move_and_attack()

    def handle_enemy_actions(self):
        for enemy in list(self.enemies):
            enemy.find_target(self.tanks)
            enemy.move_and_attack()
            if enemy.rect.x > SCREEN_WIDTH:
                self.escaped_enemies += 1
                enemy.kill()

    def draw_ui(self):
        resources_text = FONT.render(f"Resources: {self.resources}", True, WHITE)
        upgrade_points_text = FONT.render(f"Upgrade Points: {upgrade_points}", True, WHITE)
        wave_text = FONT.render(f"Wave: {self.wave}", True, WHITE)
        escaped_text = FONT.render(f"Escaped: {self.escaped_enemies}/{MAX_ESCAPED_ENEMIES}", True, WHITE)
        screen.blit(resources_text, (10, 10))
        screen.blit(upgrade_points_text, (10, 50))
        screen.blit(wave_text, (10, 90))
        screen.blit(escaped_text, (10, 130))
        self.tank_button.draw(screen)

    def check_game_over(self):
        if self.escaped_enemies >= MAX_ESCAPED_ENEMIES:
            return True
        return False

    def game_over_screen(self):
        screen.fill(BLACK)
        global upgrade_points
        game_over_text = FONT.render("Game Over!", True, RED)
        points_text = FONT.render(f"You earned {upgrade_points} upgrade points!", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        screen.blit(points_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(3000)  # Wait for 3 seconds before returning to main menu

    def run(self):
        running = True
        while running:
            screen.fill(BLACK)

            # Draw path
            pygame.draw.rect(screen, GRAY, (0, PATH_TOP, SCREEN_WIDTH, PATH_BOTTOM - PATH_TOP))

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.tank_button.is_clicked(event.pos):
                        self.tank_button.action()

            # Game logic
            self.generate_resources()
            self.spawn_enemy()
            self.handle_tank_actions()
            self.handle_enemy_actions()
            self.check_wave_end()

            # Draw everything
            self.tanks.draw(screen)
            self.enemies.draw(screen)
            for tank in self.tanks:
                tank.draw_health_bar(screen)
            for enemy in self.enemies:
                enemy.draw_health_bar(screen)
            self.draw_ui()

            if self.check_game_over():
                self.game_over_screen()
                running = False  # Exit the game loop to return to main menu

            pygame.display.flip()
            clock.tick(FPS)


def main_menu():
    start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, "Start Game", "start")
    quit_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50, "Quit", "quit")

    while True:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(event.pos):
                    game = Game()
                    game.run()
                elif quit_button.is_clicked(event.pos):
                    pygame.quit()
                    quit()

        # Draw buttons
        start_button.draw(screen)
        quit_button.draw(screen)

        # Draw title
        title_text = FONT.render("iron Fucking Invasion", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(title_text, title_rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
