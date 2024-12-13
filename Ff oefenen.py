import pygame 
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PATH_TOP = SCREEN_HEIGHT - 200
PATH_BOTTOM = SCREEN_HEIGHT - 50
FPS = 60
TANK_COST = 50
BASE_TANK_DAMAGE = 10
BASE_TANK_HEALTH = 100
ENEMY_DAMAGE = 10
ENEMY_HEALTH = 100
MAX_ESCAPED_ENEMIES = 10
FONT = pygame.font.Font(None, 36)
FONTTITLE = pygame.font.Font(None, 80)
RESOURCE_GENERATION_INTERVAL = 1000  # 1 second

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 100, 0,)
BLUE = (0, 0, 255)
DARKBLUE = (0, 18, 154)
SKYBLUE = (22, 65, 124)
GRAY = (128, 128, 128)

# Upgrade Variables
upgrade_points = 0
tank_damage_upgrade = 0
tank_health_upgrade = 0

# Game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load background image
background_image = pygame.image.load("background.png").convert()
lobby_image= pygame.image.load("SterrenAchtergrond.png").convert()

# Classes
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Father.png").convert_alpha()  
        self.image = pygame.transform.scale(self.image, (200, 120))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_health = BASE_TANK_HEALTH + tank_health_upgrade + 10  # Opslaan van maximale gezondheid
        self.health = self.max_health
        self.damage = BASE_TANK_DAMAGE + tank_damage_upgrade + 2
        self.speed = 2
        self.target = None

    def draw_health_bar(self, screen):
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / self.max_health
        bar_color = GREEN if health_ratio > 0.5 else RED
        pygame.draw.rect(screen, GRAY, (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (self.rect.centerx - bar_width // 2, self.rect.top - 10, int(bar_width * health_ratio), bar_height))

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
        bar_width = 30
        bar_height = 5
        max_health = BASE_TANK_HEALTH + tank_health_upgrade + 10
        health_ratio = self.health / max_health
        bar_color = GREEN if health_ratio > 0.5 else RED
        pygame.draw.rect(screen, GRAY, (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (self.rect.centerx - bar_width // 2, self.rect.top - 10, int(bar_width * health_ratio), bar_height))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, damage):
        super().__init__()
        self.image = pygame.image.load("SigaretKogel.png").convert_alpha()  
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Stel de startpositie in
        self.target = target
        self.speed = 5
        self.damage = damage


    def update(self):
        if self.target and self.target.alive():
            # Beweeg de kogel richting de vijand
            dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                dx, dy = dx / distance, dy / distance
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            # Controleer of de kogel de vijand raakt
            if self.rect.colliderect(self.target.rect):
                self.target.health -= self.damage
                if self.target.health <= 0:
                    self.target.kill()
                self.kill()  # Verwijder de kogel
        else:
            self.kill()  # Verwijder de kogel als er geen doelwit meer is


# In de RangedTank klasse
class RangedTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load("LuckyLuke.png").convert_alpha()  
        self.image = pygame.transform.scale(self.image, (80, 100))
        self.max_health = 50
        self.health = self.max_health
        self.damage = 34  # Dubbele schade ten opzichte van de gewone tank (stel dat gewone tank 10 heeft)
        self.range = 150
        self.cooldown = 750 # Tijd in milliseconden tussen schoten
        self.speed = 1  # Houd dezelfde snelheid

        self.last_shot_time = pygame.time.get_ticks()

    def draw_health_bar(self, screen):
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / self.max_health
        bar_color = GREEN if health_ratio > 0.5 else RED
        # Plaats de healthbar direct boven het midden van de afbeelding
        bar_x = self.rect.left + 20
        bar_y = self.rect.top - bar_height - 5
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))


    def move_and_attack(self, projectiles_group):
        current_time = pygame.time.get_ticks()
        if self.target:
            # Beweeg niet te dicht naar de vijand, blijf binnen afstand
            distance = math.hypot(self.rect.centerx - self.target.rect.centerx, self.rect.centery - self.target.rect.centery)
            if distance > self.range:
                # Beweeg richting de vijand
                dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
                if distance > 0:
                    dx, dy = dx / distance, dy / distance
                    self.rect.x += dx * self.speed
                    self.rect.y += dy * self.speed

            # Schiet als de vijand binnen bereik is
            elif distance <= self.range and current_time - self.last_shot_time >= self.cooldown:
                projectile = Projectile(self.rect.centerx, self.rect.centery, self.target, self.damage)
                projectiles_group.add(projectile)  # Voeg de kogel toe aan de groep projectielen
                self.last_shot_time = current_time
                if distance < 150:
                    self.target.health -= self.damage
                    global upgrade_points
                    upgrade_points += 1  # Earn an upgrade point
                    self.target.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, health, damage):
        super().__init__()
        self.image = pygame.image.load("R2D2.png").convert_alpha() 
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))
        self.max_health = health  # Opslaan van maximale gezondheid
        self.health = self.max_health
        self.damage = damage
        self.max_health = health  
        self.speed = speed
        self.target = None

    def draw_health_bar(self, screen):
        bar_width = 30
        bar_height = 5
        health_ratio = self.health / self.max_health
        bar_color = GREEN if health_ratio > 0.5 else RED
        pygame.draw.rect(screen, GRAY, (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (self.rect.centerx - bar_width // 2, self.rect.top - 10, int(bar_width * health_ratio), bar_height))


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

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = SKYBLUE
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
        self.enemies_to_spawn = 5
        self.spawned_enemies = 0
        self.enemy_health_multiplier = 1.0
        self.enemy_damage_multiplier = 1.0
        self.enemy_speed_multiplier = 1.0
        self.projectile = pygame.sprite.Group()  # Groep voor alle projectielen
        self.tank_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 140, 40, "Place Tank", lambda: self.place_tank())
        self.ranged_tank_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 40, "Place Ranged", lambda: self.place_ranged_tank())


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
                damage = ENEMY_DAMAGE * self.enemy_damage_multiplier
                enemy = Enemy(0, y, speed, health, damage)
                self.enemies.add(enemy)
                self.spawned_enemies += 1

    def check_wave_end(self):
        if self.spawned_enemies == self.enemies_to_spawn and len(self.enemies) == 0:
            self.wave_active = False
            self.start_new_wave()

    def start_new_wave(self):
        self.wave += 1
        self.enemy_health_multiplier += 0.2
        self.enemy_damage_multiplier += 0.1
        self.enemy_speed_multiplier += 0.1
        self.enemies_to_spawn += 3
        self.spawned_enemies = 0
        self.wave_active = True

    def place_ranged_tank(self):
        if self.resources >= TANK_COST:
            x = random.randint(SCREEN_WIDTH - 100, SCREEN_WIDTH - 40)
            y = random.randint(PATH_TOP, PATH_BOTTOM)
            ranged_tank = RangedTank(x, y)
            self.tanks.add(ranged_tank)
            self.resources -= TANK_COST

    def place_tank(self):
        if self.resources >= TANK_COST:
            x = random.randint(SCREEN_WIDTH - 100, SCREEN_WIDTH - 40)
            y = random.randint(PATH_TOP, PATH_BOTTOM)
            tank = Tank(x, y)
            self.tanks.add(tank)
            self.resources -= TANK_COST

    def handle_tank_actions(self):
        for tank in list(self.tanks):
            tank.find_target(self.enemies)
            if isinstance(tank, RangedTank):
                tank.move_and_attack(self.projectile)  # Geef de groep projectielen door
            else:
                tank.move_and_attack()

            # Controleer of een tank de linkerzijde bereikt
            if tank.rect.x <= -90:
                self.escaped_enemies -= 1  # Verminder het aantal ontsnapte vijanden
                tank.kill()  # Verwijder de tank
            if tank.rect.x <= -90:
                self.escaped_enemies = max(0, self.escaped_enemies - 1)  # Zorg ervoor dat het niet onder 0 komt
                tank.kill()  # Verwijder de tank

    def handle_enemy_actions(self):
        for enemy in list(self.enemies):
            enemy.find_target(self.tanks)
            enemy.move_and_attack()
            if enemy.rect.x > SCREEN_WIDTH:
                self.escaped_enemies += 1
                enemy.kill()

    def draw_ui(self):
        resources_text = FONT.render(f"Resources: {self.resources}", True, BLACK)
        upgrade_points_text = FONT.render(f"Upgrade Points: {upgrade_points}", True, BLACK)
        wave_text = FONT.render(f"Wave: {self.wave}", True, BLACK)
        escaped_text = FONT.render(f"Escaped: {self.escaped_enemies}/{MAX_ESCAPED_ENEMIES}", True, BLACK)
        screen.blit(resources_text, (10, 10))
        screen.blit(upgrade_points_text, (10, 50))
        screen.blit(wave_text, (10, 90))
        screen.blit(escaped_text, (10, 130))
        self.tank_button.draw(screen)
        self.ranged_tank_button.draw(screen)

    def check_game_over(self):
        if self.escaped_enemies >= MAX_ESCAPED_ENEMIES:
            return True
        return False

    def game_over_screen(self):
        screen.blit(lobby_image, (0, -200)) 
        global upgrade_points
        game_over_text = FONTTITLE.render("Game Over!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        points_text = FONT.render(f"You earned {upgrade_points} upgrade points!", True, WHITE)
        points_rect = points_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(game_over_text, game_over_rect)
        screen.blit(points_text, points_rect)
        pygame.display.flip()
        pygame.time.delay(3000)
        main_menu()

    def run(self):
        running = True
        while running:
            # Use the background image for the screen
            pygame.draw.rect(screen, DARKGREEN, (0, PATH_TOP, SCREEN_WIDTH, PATH_BOTTOM - PATH_TOP))
            screen.blit(background_image, (0, 0))  # Draw background at top-left corner

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.tank_button.is_clicked(event.pos):
                        self.tank_button.action()
                    elif self.ranged_tank_button.is_clicked(event.pos):
                        self.ranged_tank_button.action()

            # Game logic
            self.generate_resources()
            self.spawn_enemy()
            self.handle_tank_actions()
            self.handle_enemy_actions()
            self.projectile.update()  # Update alle projectielen
            self.check_wave_end()

            # Draw everything
            self.tanks.draw(screen)
            self.enemies.draw(screen)
            self.projectile.draw(screen)  # Teken alle projectielen
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

def upgrade_menu():
    global tank_damage_upgrade, tank_health_upgrade, upgrade_points

    damage_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, "Upgrade Damage (2 pts)", "damage")
    health_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50, "Upgrade Health (2 pts)", "health")
    back_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50, "Back", "back")

    while True:
        screen.blit(lobby_image, (0, -200))  
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if damage_button.is_clicked(event.pos) and upgrade_points >= 2:
                    tank_damage_upgrade += 1
                    upgrade_points -= 2
                elif health_button.is_clicked(event.pos) and upgrade_points >= 2:
                    tank_health_upgrade += 1
                    upgrade_points -= 2
                elif back_button.is_clicked(event.pos):
                    return

        # Draw buttons
        damage_button.draw(screen)
        health_button.draw(screen)
        back_button.draw(screen)

        # Draw upgrade status
        total_damage = BASE_TANK_DAMAGE + tank_damage_upgrade * 2
        total_health = BASE_TANK_HEALTH + tank_health_upgrade * 10

        status_text = FONT.render(f"Upgrade Points: {upgrade_points}", True, WHITE)
        damage_text = FONT.render(f"Total Damage: {total_damage}", True, WHITE)
        health_text = FONT.render(f"Total Health: {total_health}", True, WHITE)

        screen.blit(status_text, (10, 10))
        screen.blit(damage_text, (10, 50))
        screen.blit(health_text, (10, 90))

        pygame.display.flip()
        clock.tick(FPS)

def main_menu():
    start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, "Start Game", "start")
    upgrade_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50, "Upgrades", "upgrades")
    quit_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50, "Quit", "quit")
    screen.blit(lobby_image, (0, -200)) 
    while True:

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(event.pos):
                    game = Game()
                    game.run()
                elif upgrade_button.is_clicked(event.pos):
                    upgrade_menu()
                elif quit_button.is_clicked(event.pos):
                    pygame.quit()
                    quit()

        # Draw buttons
        start_button.draw(screen)
        upgrade_button.draw(screen)
        quit_button.draw(screen)

        # Draw title
        title_text = FONTTITLE.render("Iron Invasion", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(title_text, title_rect)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main_menu()
    