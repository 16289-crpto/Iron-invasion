import pygame
import sys
import random

# Initialiseer Pygame
pygame.init()

# Maak een venster
screen = pygame.display.set_mode((800, 600))  # Resolutie: 800x600
pygame.display.set_caption("Iron Invasion")

clock = pygame.time.Clock()
fps = 60

# Kleuren definiëren
zwart = (0, 0, 0)
wit = (255, 255, 255)
rood = (255, 0, 0)
groen = (0, 255, 0)
iets = (200, 12, 60)

# Globale variabelen
coins = 0
blocks = []  # Lijst om blokken op te slaan
last_coin_time = pygame.time.get_ticks()  # Tijd sinds laatste coin-generatie

# Functie om blokken te spawnen
def spawn_block():
    new_block = pygame.Rect(0, random.randint(50, 550), 50, 50)  # Spawn aan de linkerkant
    blocks.append(new_block)

# Hoofdlus
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Controleer op afsluiten
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and coins >= 5:  # Spawnt een blok met 5 coins
                spawn_block()
                coins -= 5  # Verminder coins met 5

    # Coins genereren elke 2 seconden
    current_time = pygame.time.get_ticks()
    if current_time - last_coin_time > 2000:  # 2000 ms = 2 seconden
        coins += 1
        last_coin_time = current_time

    # Update blokken
    for block in blocks:
        block.x += 5  # Beweeg blok naar rechts
    blocks = [block for block in blocks if block.x < 800]  # Verwijder blokken die buiten beeld zijn

    # Collision detectie tussen blokken
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            if blocks[i].colliderect(blocks[j]):
                print("Blokken botsen!")
                # Optioneel: voeg gedrag toe bij botsing

    # Scherm vullen met kleur
    screen.fill(iets)

    # Teken blokken
    for block in blocks:
        pygame.draw.rect(screen, rood, block)

    # Coins weergeven
    font = pygame.font.SysFont(None, 36)
    coin_text = font.render(f"Coins: {coins}", True, wit)
    screen.blit(coin_text, (10, 10))

    # Werk het scherm bij
    pygame.display.flip()
    clock.tick(fps)

# Sluit Pygame af
pygame.quit()
sys.exit()