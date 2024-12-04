import pygame
import sys

# Initialiseer Pygame
pygame.init()

# Maak een venster
screen = pygame.display.set_mode((800, 600))  # Resolutie: 800x600
pygame.display.set_caption("Iron Invasion")

pygame.time.Clock()
fps = 60

# Kleuren definiëren
zwart = (0,0,0)
wit = (255, 255, 255)
rood = (255,0,0)
blauw = (0,0,255)
groen = (0,255,0)
iets = (200,12,60)

#Globale bs
coins = 0

# Hoofdlus
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Controleer op afsluiten
            running = False

    #Coins geven
    current_time = pygame.time.get_ticks()
    if current_time - last_iron_time > 2000:  # 2000 ms = 2 seconden
        iron += 1
        last_iron_time = current_time

    # Scherm vullen met wit
    screen.fill(iets)

    # Werk het scherm bij
    pygame.display.flip()

# Sluit Pygame af
pygame.quit()
sys.exit()