"""Main module for the English Battle game."""
from typing import Optional

import pygame
import random
import sys
from pygame import Surface
from pygame.time import Clock

from lib.Color import Color
from lib.Core import Hero, Zombie, Character
from lib.Level import Level, Combat, LevelType

pygame.init()

DEFAULT_WINDOW_SIZE: tuple[int, int] = (640, 480)
window: Surface = pygame.display.set_mode(DEFAULT_WINDOW_SIZE)
pygame.display.set_caption("English Battle")
character: Character = Hero(50, 50, health=20)

level_difficulty = 2
NUM_ZOMBIES: int = 5
level: Level = Level(DEFAULT_WINDOW_SIZE, difficulty=level_difficulty,
                     level_type=LevelType.WORD_ORDERING)
zombies: list[Zombie] = level.generate_zombies(NUM_ZOMBIES)

repeat: bool = True
# Para limitar los FPS
clock: Clock = pygame.time.Clock()

# Para controlar el movimiento aleatorio de los zombies
ZOMBIE_MOVE_INTERVAL: int = 10
zombie_move_counter: int = 0

# Para detectar pulsación de la tecla
attack_pressed: bool = False

combat_instance: Optional[Combat] = None
combat_input_text = ""
combat_result_text = ""
font = pygame.font.SysFont("Roboto", 24)


def handle_events() -> None:
  """Handles all pygame events."""
  global repeat, combat_input_text, combat_result_text
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      repeat = False
    # Delegar eventos de combate y modal a Level
    level.handle_combat_event(event, font)
    # Input por teclado solo si hay combate y no es word_ordering
    combat_instance = level.get_combat_instance()
    if combat_instance is not None and combat_instance.active and (
        combat_instance.current_type != "word_ordering"):
      handle_combat_input(event)


def handle_combat_input(event) -> None:
  """Combat input handling."""
  global combat_instance, combat_input_text, combat_result_text
  if combat_instance is not None and combat_instance.active:
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RETURN:
        if combat_input_text.strip():
          character.update_sprite_after_damage()
          for zombie in zombies:
            zombie.update_sprite_after_damage()
          draw_game()
          combat_result_text = combat_instance.process_turn(combat_input_text)
          combat_input_text = ""
      elif event.key == pygame.K_BACKSPACE:
        combat_input_text = combat_input_text[:-1]
      else:
        char = event.unicode
        if char.isprintable():
          combat_input_text += char


def move_character() -> None:
  """Moves the hero based on key presses."""
  global character, zombies, combat_instance
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

  # Solo permite movimiento si no hay combate activo
  if combat_instance is None or not combat_instance.active:
    character.move(dx, dy, moving, DEFAULT_WINDOW_SIZE[0],
                   DEFAULT_WINDOW_SIZE[1],
                   level=level, other_characters=zombies)
  # Si hay combate, nadie se mueve (ni héroe ni zombies)


def handle_combat_trigger() -> None:
  """Detects and initiates combat if the hero is near a zombie."""
  global combat_result_text, combat_input_text
  started = level.start_combat(character, zombies, font)
  if started:
    combat_result_text = ""
    combat_input_text = ""


def handle_attack() -> None:
  """Handles the attack action when the attack key is pressed."""
  global attack_pressed, character, zombies, combat_instance
  keys = pygame.key.get_pressed()
  if keys[pygame.K_x]:
    if not attack_pressed and (
        combat_instance is None or not combat_instance.active):
      target = _find_attackable_zombie()
      if target:
        character.attack(target)
      else:
        closest = _find_closest_zombie()
        if closest:
          character.attack(closest)
      attack_pressed = True
  else:
    attack_pressed = False


def _find_attackable_zombie() -> Optional[Zombie]:
  """Finds the closest zombie within attack range."""
  min_dist = float('inf')
  target = None
  for zombie in zombies:
    if zombie.is_alive():
      hero_center = (character.x + 23 // 2, character.y + 30 // 2)
      zombie_center = (zombie.x + 23 // 2, zombie.y + 30 // 2)
      dist = ((hero_center[0] - zombie_center[0]) ** 2 +
              (hero_center[1] - zombie_center[1]) ** 2) ** 0.5
      if dist <= character.attack_range and dist < min_dist:
        target = zombie
        min_dist = dist
  return target


def _find_closest_zombie() -> Optional[Zombie]:
  """Finds the closest zombie (regardless of range)."""
  min_dist = float('inf')
  closest = None
  for zombie in zombies:
    if zombie.is_alive():
      hero_center = (character.x + 23 // 2, character.y + 30 // 2)
      zombie_center = (zombie.x + 23 // 2, zombie.y + 30 // 2)
      dist = ((hero_center[0] - zombie_center[0]) ** 2 +
              (hero_center[1] - zombie_center[1]) ** 2) ** 0.5
      if dist < min_dist:
        closest = zombie
        min_dist = dist
  return closest


def move_zombies() -> None:
  """Moves the zombies randomly at set intervals."""
  global zombie_move_counter, zombies, character, combat_instance
  zombie_move_counter += 1
  if zombie_move_counter >= ZOMBIE_MOVE_INTERVAL:
    if combat_instance is None or not combat_instance.active:
      for zombie in zombies:
        if not zombie.is_alive():
          continue
        zdx, zdy = 0, 0
        direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
        zdx, zdy = direction
        if zdx != 0 or zdy != 0:
          other_chars = [character] + [z for z in zombies if z is not zombie]
          zombie.move(zdx, zdy, True, DEFAULT_WINDOW_SIZE[0],
                      DEFAULT_WINDOW_SIZE[1], level=level,
                      other_characters=other_chars)
    zombie_move_counter = 0


def draw_game() -> None:
  """Draws all game elements on the window."""
  window.fill((255, 255, 255))
  level.draw_background(window)
  level.draw_maze(window)
  for zombie in zombies:
    if not zombie.is_alive():
      zombie.draw(window)
  character.draw(window)
  for zombie in zombies:
    if zombie.is_alive():
      zombie.draw(window)

  # Interfaz gráfica para combate
  combat_instance = level.get_combat_instance()
  word_ordering_modal = level.get_combat_modal()
  if combat_instance is not None and combat_instance.active:
    overlay = pygame.Surface(DEFAULT_WINDOW_SIZE)
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    window.blit(overlay, (0, 0))
    if combat_instance.current_type == "word_ordering" and word_ordering_modal:
      word_ordering_modal.draw(window)
    else:
      question_text = f"Ordena la oración correctamente: {combat_instance.current_question}"
      question_surface = font.render(question_text, True,
                                     Color.QUESTION_SURFACE_BG)
      window.blit(question_surface, (40, 100))
      input_surface = font.render("Tu respuesta: " + combat_input_text, True,
                                  Color.ANSWER_SURFACE_BG)
      window.blit(input_surface, (40, 150))
      if combat_result_text:
        result_surface = font.render(combat_result_text, True,
                                     Color.CORRECT_ANSWER_BG if "Correcto" in combat_result_text else Color.WRONG_ANSWER_BG)
        window.blit(result_surface, (40, 200))
  pygame.display.flip()


def update_all_sprites() -> None:
  """Updates all character sprites."""
  character.update_sprite_after_damage()
  for zombie in zombies:
    zombie.update_sprite_after_damage()


def main_loop() -> None:
  """Main game loop."""
  global repeat
  while repeat:
    if not character.is_alive():
      level.handle_player_death(window)
      clock.tick(60)
      continue
    handle_events()
    move_character()
    handle_combat_trigger()
    handle_attack()
    move_zombies()
    update_all_sprites()
    draw_game()
    clock.tick(60)
  pygame.quit()
  sys.exit()


if __name__ == "__main__":
  main_loop()
