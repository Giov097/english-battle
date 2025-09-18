"""Main module for the English Battle game."""

import pygame
import sys
import random

from lib.Core import Hero, Zombie
from lib.Level import Level

pygame.init()

DEFAULT_WINDOW_SIZE = (640, 480)
window = pygame.display.set_mode(DEFAULT_WINDOW_SIZE)
pygame.display.set_caption("English Battle")
# Nueva posición inicial
character = Hero(50, 50)
level = Level(DEFAULT_WINDOW_SIZE)


# Spawnea zombies en posiciones válidas
def get_valid_spawn(lvl: Level, window_size: tuple[int, int]) -> tuple[
  int, int]:
  """Generates a valid spawn position."""
  sprite_w, sprite_h = (23, 30)
  while True:
    x = random.randint(0, window_size[0] - sprite_w)
    y = random.randint(0, window_size[1] - sprite_h)
    rect = pygame.Rect(x, y, sprite_w, sprite_h)
    if not lvl.check_collision(rect):
      return x, y


NUM_ZOMBIES = 5
zombies = []
for _ in range(NUM_ZOMBIES):
  zx, zy = get_valid_spawn(level, DEFAULT_WINDOW_SIZE)
  zombies.append(Zombie(zx, zy))

repeat = True
# Para limitar los FPS
clock = pygame.time.Clock()

# Para controlar el movimiento aleatorio de los zombies
ZOMBIE_MOVE_INTERVAL = 10  # frames
zombie_move_counter = 0

while repeat:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      repeat = False

  keys = pygame.key.get_pressed()
  moving = False
  dx, dy = 0, 0
  if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
    dx = -1
    moving = True
  if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
    dx = 1
    moving = True
  if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
    dy = -1
    moving = True
  if keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
    dy = 1
    moving = True

  character.move(dx, dy, moving, DEFAULT_WINDOW_SIZE[0], DEFAULT_WINDOW_SIZE[1],
                 level=level, other_characters=zombies)

  # Movimiento aleatorio de zombies cada cierto intervalo
  zombie_move_counter += 1
  if zombie_move_counter >= ZOMBIE_MOVE_INTERVAL:
    for zombie in zombies:
      zdx, zdy = 0, 0
      # Elige una dirección aleatoria (pero no diagonal)
      direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
      zdx, zdy = direction
      # Solo mueve si hay dirección
      if zdx != 0 or zdy != 0:
        # Los zombies consideran al héroe y a los otros zombies para colisión
        other_chars = [character] + [z for z in zombies if z is not zombie]
        zombie.move(zdx, zdy, True, DEFAULT_WINDOW_SIZE[0],
                    DEFAULT_WINDOW_SIZE[1], level=level,
                    other_characters=other_chars)
    zombie_move_counter = 0

  window.fill((255, 255, 255))
  level.draw_background(window)
  level.draw_maze(window)
  character.draw(window)
  for zombie in zombies:
    zombie.draw(window)
  pygame.display.flip()
  # Limita a 60 FPS
  clock.tick(60)

pygame.quit()
sys.exit()
