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
attack_pressed = False  # Para detectar pulsación de la tecla

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

  # Ataque del héroe solo si se presiona la tecla "x" (no sostenida)
  if keys[pygame.K_x]:
    if not attack_pressed:
      target = None
      min_dist = float('inf')
      for zombie in zombies:
        if not zombie.dead:
          # Calcula distancia al centro
          hero_center = (
            character.x + 23 // 2,
            character.y + 30 // 2
          )
          zombie_center = (
            zombie.x + 23 // 2,
            zombie.y + 30 // 2
          )
          dist = ((hero_center[0] - zombie_center[0]) ** 2 +
                  (hero_center[1] - zombie_center[1]) ** 2) ** 0.5
          if dist <= character.attack_range and dist < min_dist:
            target = zombie
            min_dist = dist
      if target:
        character.attack(target)
      else:
        closest = None
        min_dist = float('inf')
        for zombie in zombies:
          if not zombie.dead:
            hero_center = (
              character.x + 23 // 2,
              character.y + 30 // 2
            )
            zombie_center = (
              zombie.x + 23 // 2,
              zombie.y + 30 // 2
            )
            dist = ((hero_center[0] - zombie_center[0]) ** 2 +
                    (hero_center[1] - zombie_center[1]) ** 2) ** 0.5
            if dist < min_dist:
              closest = zombie
              min_dist = dist
        if closest:
          character.attack(closest)
      attack_pressed = True
  else:
    attack_pressed = False

  # Movimiento aleatorio de zombies cada cierto intervalo
  # zombie_move_counter += 1
  # if zombie_move_counter >= ZOMBIE_MOVE_INTERVAL:
  #   for zombie in zombies:
  #     if zombie.dead:
  #       continue
  #     zdx, zdy = 0, 0
  #     direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
  #     zdx, zdy = direction
  #     if zdx != 0 or zdy != 0:
  #       other_chars = [character] + [z for z in zombies if z is not zombie]
  #       zombie.move(zdx, zdy, True, DEFAULT_WINDOW_SIZE[0],
  #                   DEFAULT_WINDOW_SIZE[1], level=level,
  #                   other_characters=other_chars)
  #     # Ataque zombie al héroe si está en rango y cooldown expirado
  #     if not character.dead and zombie.can_attack(character):
  #       zombie.attack(character)
  #   zombie_move_counter = 0

  window.fill((255, 255, 255))
  level.draw_background(window)
  level.draw_maze(window)
  character.draw(window)
  for zombie in zombies:
    zombie.draw(window)
  pygame.display.flip()
  clock.tick(60)

pygame.quit()
sys.exit()
