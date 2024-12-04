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
wit = (255, 255, 255)

# Hoofdlus
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Controleer op afsluiten
            running = False

    # Scherm vullen met wit
    screen.fill(wit)

    # Werk het scherm bij
    pygame.display.flip()

# Sluit Pygame af
pygame.quit()
sys.exit()