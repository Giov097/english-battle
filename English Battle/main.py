"""Main module for the English Battle game."""
import random
from typing import Optional

import pygame
from pygame import Surface
from pygame.time import Clock

from font import FONTS
from lib.combat import Combat
from lib.functions import transition_black_screen, \
  close_game, find_attackable_zombie, find_closest_zombie, \
  draw_game, main_menu, check_advance_level, play_music, update_all_sprites
from lib.level import FeedbackBox
from lib.var import Var

pygame.init()

window: Surface = pygame.display.set_mode(Var.DEFAULT_WINDOW_SIZE)
pygame.display.set_caption("English Battle")

repeat: bool = True
clock: Clock = pygame.time.Clock()

ZOMBIE_MOVE_INTERVAL: int = 10
zombie_move_counter: int = 0

attack_pressed: bool = False

combat_instance: Optional[Combat] = None
combat_input_text = ""
combat_result_text = ""
font = pygame.font.Font(FONTS.get("roboto"), 16)

feedbackBox = FeedbackBox.get_instance()
first_level: bool = True
current_level_idx: int


def handle_events() -> None:
  """Handles all pygame events."""
  global repeat, combat_input_text, combat_result_text
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      repeat = False
    pause_result = Var.level.handle_pause_event(event)
    if Var.level.get_pause_menu() and pause_result == "main_menu":
      main_menu(window)
    Var.level.handle_combat_event(event, font)
    combat = Var.level.get_combat_instance()
    if combat is not None and combat.get_active():
      handle_combat_input(event)


def handle_combat_input(event) -> None:
  """Combat input handling."""
  global combat_instance, combat_input_text, combat_result_text
  if combat_instance is not None and combat_instance.get_active():
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RETURN:
        if combat_input_text.strip():
          character.update_sprite_after_damage()
          for zombie in zombies:
            zombie.update_sprite_after_damage()
          draw_game(Var.level, window, character, zombies)
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
  global combat_instance
  if not Var.level.get_pause_menu().get_active():
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

    combat_instance = Var.level.get_combat_instance()
    if combat_instance is None or not combat_instance.get_active():
      Var.character.move(dx, dy, moving, Var.DEFAULT_WINDOW_SIZE[0],
                         Var.DEFAULT_WINDOW_SIZE[1],
                         level=Var.level, other_characters=Var.zombies)
    # Si hay combate, nadie se mueve (ni héroe ni zombies)
    else:
      # Bloquea movimiento del héroe y zombies durante combate
      pass


def handle_combat_trigger() -> None:
  """Detects and initiates combat if the hero is near a zombie."""
  global combat_result_text, combat_input_text
  started = Var.level.start_combat(Var.character, Var.zombies, font)
  if started:
    combat_result_text = ""
    combat_input_text = ""


def handle_attack() -> None:
  """Handles the attack action when the attack key is pressed."""
  global attack_pressed, character, zombies, combat_instance
  keys = pygame.key.get_pressed()
  if keys[pygame.K_x]:
    if not attack_pressed and (
        combat_instance is None or not combat_instance.get_active()):
      target = find_attackable_zombie(character, zombies)
      if target:
        character.attack(target)
      else:
        closest = find_closest_zombie(character, zombies)
        if closest:
          character.attack(closest)
      attack_pressed = True
  else:
    attack_pressed = False


def move_zombies() -> None:
  """Moves the zombies randomly at set intervals."""
  global zombie_move_counter, combat_instance
  if not Var.level.get_pause_menu().get_active():
    zombie_move_counter += 1
    if zombie_move_counter >= ZOMBIE_MOVE_INTERVAL:
      combat_instance = Var.level.get_combat_instance()
      if combat_instance is None or not combat_instance.get_active():
        for zombie in Var.zombies:
          if not zombie.is_alive():
            continue
          zdx, zdy = 0, 0
          direction = random.choice(
              [(15, 0), (-15, 0), (0, 15), (0, -15), (0, 0)])
          zdx, zdy = direction
          if zdx != 0 or zdy != 0:
            other_chars = [Var.character] + [z for z in Var.zombies if
                                             z is not zombie]
            zombie.move(zdx, zdy, True, Var.DEFAULT_WINDOW_SIZE[0],
                        Var.DEFAULT_WINDOW_SIZE[1], level=Var.level,
                        other_characters=other_chars)
      zombie_move_counter = 0


def main_loop() -> None:
  """Main game loop."""
  global repeat, window
  play_music()
  main_menu(window)
  while repeat:
    if not Var.character.is_alive():
      Var.level.play_death_sounds()
      transition_black_screen(window, 3)
      main_menu(window)
    handle_events()
    move_character()
    handle_combat_trigger()
    handle_attack()
    move_zombies()
    update_all_sprites(Var.character, Var.zombies)
    Var.level.check_open_door(Var.zombies)
    Var.level.check_medkit_pickup()
    check_advance_level(Var.level, Var.character, window)
    draw_game(Var.level, window, Var.character, Var.zombies)
    clock.tick(60)
  close_game()


if __name__ == "__main__":
  main_loop()
