import pygame
import sys

from lib.Core import Hero
from Sprite.Backgrounds import BACKGROUNDS

pygame.init()

window_size = (640, 480)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("English Battle")
character = Hero(300, 220)

background = BACKGROUNDS["grass"]
background = pygame.transform.scale(background, window_size)

repeat = True
clock = pygame.time.Clock()  # Para limitar los FPS

while repeat:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      repeat = False

  keys = pygame.key.get_pressed()
  moving = False
  dx, dy = 0, 0
  if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
    dx = -5
    moving = True
  if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
    dx = 5
    moving = True
  if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
    dy = -5
    moving = True
  if keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
    dy = 5
    moving = True

  character.move(dx, dy, moving, window_size[0], window_size[1])

  window.fill((255, 255, 255))
  window.blit(background, (0, 0))  # Dibuja el fondo
  character.draw(window)
  pygame.display.flip()
  clock.tick(60)  # Limita a 60 FPS

pygame.quit()
sys.exit()
