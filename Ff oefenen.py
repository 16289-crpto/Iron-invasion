import pygame 
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PATH_TOP = SCREEN_HEIGHT - 225
PATH_BOTTOM = SCREEN_HEIGHT - 75
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
ranged_tank_damage_upgrade = 0
ranged_tank_health_upgrade = 0

damage_upgrade_cost = 2
health_upgrade_cost = 2
ranged_damage_upgrade_cost = 2
ranged_health_upgrade_cost = 2

# Voeg dit toe aan het begin van je script
ranger_unlocked = False

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
        self.max_health = BASE_TANK_HEALTH + tank_health_upgrade * 10  # Opslaan van maximale gezondheid
        self.health = self.max_health
        self.damage = BASE_TANK_DAMAGE + tank_damage_upgrade * 2
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
                    if isinstance(self.target, Enemy):  # Alleen punten voor vijanden
                        global upgrade_points
                        upgrade_points += 1
                    self.target.kill()
        else:
            # No target, move left
            self.rect.x -= self.speed

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
        else:
            # No target, move left
            self.rect.x -= self.speed

    def draw_health_bar(self, screen):
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / self.max_health
        bar_color = GREEN if health_ratio > 0.5 else RED
        pygame.draw.rect(screen, GRAY, (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (self.rect.centerx - bar_width // 2, self.rect.top - 10, int(bar_width * health_ratio), bar_height))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, damage, shooter):
        super().__init__()
        self.image = pygame.image.load("SigaretKogel.png").convert_alpha()  
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Stel de startpositie in
        self.target = target
        self.speed = 7
        self.damage = damage
        self.shooter = shooter  # De tank die de kogel heeft afgeschoten

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
                    if isinstance(self.shooter, (Tank, RangedTank)) and isinstance(self.target, Enemy):
                        global upgrade_points
                        upgrade_points += 1  # Alleen als een tank een vijand doodt
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
        self.rect = self.image.get_rect(center=(x, y))  
        self.max_health = 50 + ranged_tank_health_upgrade * 5
        self.health = self.max_health
        self.damage = 34 + ranged_tank_damage_upgrade * 3
        self.range = 150
        self.cooldown = 500
        self.speed = 1
        self.last_shot_time = pygame.time.get_ticks()

    def draw_health_bar(self, screen):
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / self.max_health
        bar_color = GREEN if health_ratio > 0.5 else RED
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
                projectile = Projectile(self.rect.centerx, self.rect.centery, self.target, self.damage, self)
                projectiles_group.add(projectile)  # Voeg de kogel toe aan de groep projectielen
                self.last_shot_time = current_time
        else:
            # No target, move left
            self.rect.x -= self.speed
    
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

# Basiswaarden voor de EnemyRanger
base_health_eranger = 50
base_damage_eranger = 34

class EnemyRanger(Enemy):
    def __init__(self, x, y, speed, health_multiplier, damage_multiplier):
        # Bereken de verhoogde gezondheid en schade voor deze golf
        adjusted_health = base_health_eranger * health_multiplier
        adjusted_damage = base_damage_eranger * damage_multiplier
        super().__init__(x, y, speed, adjusted_health, adjusted_damage)
        self.image = pygame.image.load("EnemyRanger.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.range = 150
        self.cooldown = 750  # Schiet elke 750 ms
        self.last_shot_time = pygame.time.get_ticks()

    def move_and_attack(self, projectiles_group):
        current_time = pygame.time.get_ticks()
        if self.target:
            distance = math.hypot(self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery)
            if distance > self.range:
                dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
                if distance > 0:
                    dx, dy = dx / distance, dy / distance
                    self.rect.x += dx * self.speed
                    self.rect.y += dy * self.speed
            elif current_time - self.last_shot_time >= self.cooldown:
                projectile = Projectile(self.rect.centerx, self.rect.centery, self.target, self.damage, self)
                projectiles_group.add(projectile)
                self.last_shot_time = current_time
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
        self.tank_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 40, "Place Tank", lambda: self.place_tank())
        self.ranged_tank_button = Button(SCREEN_WIDTH - 350, SCREEN_HEIGHT - 50, 180, 40, "Place Ranged", lambda: self.place_ranged_tank())

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
                health_multiplier = self.enemy_health_multiplier
                damage_multiplier = self.enemy_damage_multiplier

                if self.wave >= 5 and random.random() < 0.3:  # 30% kans op een EnemyRanger
                    enemy = EnemyRanger(0, y, speed, health_multiplier, damage_multiplier)
                else:
                    health = ENEMY_HEALTH * health_multiplier
                    damage = ENEMY_DAMAGE * damage_multiplier
                    enemy = Enemy(0, y, speed, health, damage)
                
                self.enemies.add(enemy)
                self.spawned_enemies += 1

    def check_wave_end(self):
        if self.spawned_enemies == self.enemies_to_spawn and len(self.enemies) == 0:
            self.wave_active = False
            self.start_new_wave()

    def start_new_wave(self):
        global base_hp_Eranger, base_damage_Eranger
        self.wave += 1
        self.enemy_health_multiplier += 0.2
        self.enemy_damage_multiplier += 0.2
        self.enemy_speed_multiplier += 0.1
        self.enemies_to_spawn += 3
        self.spawned_enemies = 0
        self.wave_active = True

    def place_ranged_tank(self):
        global ranger_unlocked
        if not ranger_unlocked:
            return  # Ranger kan niet worden geplaatst als deze niet is ontgrendeld
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

            if tank.rect.x <= -90:
                self.escaped_enemies -= 1  # Verminder het aantal ontsnapte vijanden
                self.escaped_enemies = max(0, self.escaped_enemies)  # Zorg ervoor dat het niet onder 0 komt
                tank.kill()  # Verwijder de tank

    def handle_enemy_actions(self):
        for enemy in list(self.enemies):
            enemy.find_target(self.tanks)
            
            # Controleer of het een EnemyRanger is
            if isinstance(enemy, EnemyRanger):
                enemy.move_and_attack(self.projectile)  # Geef projectiles_group mee
            else:
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
        self.tank_button.draw(screen)  # Teken de standaard tank-knop

        # Controleer of de ranger is ontgrendeld voordat de knop wordt weergegeven
        if ranger_unlocked:
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
        points_text = FONT.render(f"You have a total of {upgrade_points} upgrade points!", True, WHITE)
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
    global ranged_tank_damage_upgrade, ranged_tank_health_upgrade
    global damage_upgrade_cost, health_upgrade_cost, ranged_damage_upgrade_cost, ranged_health_upgrade_cost
    global ranger_unlocked

    # Ranger ontgrendelstatus
    ranger_unlock_cost = 100
    ranger_unlocked = ranger_unlocked if 'ranger_unlocked' in globals() else False

    while True:
        screen.blit(lobby_image, (0, -200))

        # Dynamisch knopbreedte aanpassen aan de tekstlengte
        def create_dynamic_button(x, y, base_width, height, text, action, adjust_x=True, center=False):
            rendered_text = FONT.render(text, True, WHITE)
            text_width = rendered_text.get_width()
            button_width = max(base_width, text_width + 20)  # Minimaal base_width, anders tekstbreedte + padding
            button_x = x
            if adjust_x:  # Positie aanpassen aan de breedte
                button_x = x - (button_width - base_width) // 2
            if center:  # Centraal uitlijnen als vereist
                button_x = x - button_width // 2
            return Button(button_x, y, button_width, height, text, action)

        # Knoppen voor gewone tank
        damage_button = create_dynamic_button(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 100, 200, 50, f"Tank Damage ({damage_upgrade_cost} pts)", "damage", adjust_x=True)
        health_button = create_dynamic_button(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 30, 200, 50, f"Tank Health ({health_upgrade_cost} pts)", "health", adjust_x=True)

        # Knoppen voor ranged tank
        ranged_damage_button = create_dynamic_button(SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 - 100, 200, 50, f"Ranged Damage ({ranged_damage_upgrade_cost} pts)", "ranged_damage", adjust_x=True)
        ranged_health_button = create_dynamic_button(SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 - 30, 200, 50, f"Ranged Health ({ranged_health_upgrade_cost} pts)", "ranged_health", adjust_x=True)

        # Ranger ontgrendelen
        unlock_ranger_button = None
        if not ranger_unlocked:
            unlock_ranger_button = create_dynamic_button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, 300, 50, f"Unlock Ranger ({ranger_unlock_cost} pts)", "unlock_ranger", center=True)

        # Back button gecentreerd
        back_button = create_dynamic_button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200, 200, 50, "Back", "back", center=True)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Upgrades voor gewone tank
                if damage_button.is_clicked(event.pos) and upgrade_points >= damage_upgrade_cost:
                    tank_damage_upgrade += 1
                    upgrade_points -= damage_upgrade_cost
                    damage_upgrade_cost += 2
                elif health_button.is_clicked(event.pos) and upgrade_points >= health_upgrade_cost:
                    tank_health_upgrade += 1
                    upgrade_points -= health_upgrade_cost
                    health_upgrade_cost += 2
                
                # Upgrades voor ranged tank
                if ranger_unlocked:
                    if ranged_health_button.is_clicked(event.pos) and upgrade_points >= ranged_health_upgrade_cost:
                        ranged_tank_health_upgrade += 1
                        upgrade_points -= ranged_health_upgrade_cost
                        ranged_health_upgrade_cost += 2
                    elif ranged_damage_button.is_clicked(event.pos) and upgrade_points >= ranged_damage_upgrade_cost:
                        ranged_tank_damage_upgrade += 1
                        upgrade_points -= ranged_damage_upgrade_cost
                        ranged_damage_upgrade_cost += 2
                
                # Ranger ontgrendelen
                if unlock_ranger_button and unlock_ranger_button.is_clicked(event.pos) and upgrade_points >= ranger_unlock_cost:
                    ranger_unlocked = True
                    upgrade_points -= ranger_unlock_cost

                # Back naar het hoofdmenu
                if back_button.is_clicked(event.pos):
                    return

        # Knoppen tekenen
        damage_button.draw(screen)
        health_button.draw(screen)
        if unlock_ranger_button:
            unlock_ranger_button.draw(screen)
        else:
            ranged_damage_button.draw(screen)
            ranged_health_button.draw(screen)
        back_button.draw(screen)

        # Status tonen
        total_damage = BASE_TANK_DAMAGE + tank_damage_upgrade * 2
        total_health = BASE_TANK_HEALTH + tank_health_upgrade * 10
        ranged_total_damage = 34 + ranged_tank_damage_upgrade * 3
        ranged_total_health = 50 + ranged_tank_health_upgrade * 5

        status_text = FONT.render(f"Upgrade Points: {upgrade_points}", True, WHITE)
        tank_stats_text = FONT.render(f"Tank - Damage: {total_damage}, Health: {total_health}", True, WHITE)
        ranged_stats_text = FONT.render(f"Ranged Tank - Damage: {ranged_total_damage}, Health: {ranged_total_health}", True, WHITE)
        ranger_status = FONT.render(f"Ranger Unlocked: {'Yes' if ranger_unlocked else 'No'}", True, WHITE)

        screen.blit(status_text, (10, 10))
        screen.blit(tank_stats_text, (10, 50))
        screen.blit(ranged_stats_text, (10, 90))
        screen.blit(ranger_status, (10, 130))

        pygame.display.flip()


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
