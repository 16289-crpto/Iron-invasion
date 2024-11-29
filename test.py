import pygame
import random

# Initialiseer Pygame
pygame.init()

# Scherminstellingen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vang de Bal!")

# Kleuren
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Balleninstellingen
ball_radius = 20
ball_x = random.randint(ball_radius, WIDTH - ball_radius)
ball_y = random.randint(ball_radius, HEIGHT - ball_radius)

# Spelinstellingen
score = 0
font = pygame.font.Font(None, 36)

# Hoofdloop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Muisklik detectie
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    if mouse_click[0]:  # Linker muisklik
        distance = ((mouse_x - ball_x) ** 2 + (mouse_y - ball_y) ** 2) ** 0.5
        if distance < ball_radius:
            score += 1
            ball_x = random.randint(ball_radius, WIDTH - ball_radius)
            ball_y = random.randint(ball_radius, HEIGHT - ball_radius)

    # Scherm verversen
    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)

    # Score weergeven
    score_text = font.render(f'Score: {score}', True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

# Sluit Pygame af
pygame.quit()