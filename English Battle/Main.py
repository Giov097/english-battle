"""Main module for the English Battle game."""
import random
import sys
from typing import Optional

import pygame
from pygame import Surface
from pygame.font import FontType
from pygame.mixer import Channel
from pygame.time import Clock

from Sound import SOUNDS
from Sprite.Backgrounds import BACKGROUNDS
from lib.Color import Color
from lib.Core import Hero, Zombie
from lib.Level import Level, Combat, LevelType, Door
from lib.Var import FONT, LEVELS_CONFIG

pygame.init()

DEFAULT_WINDOW_SIZE: tuple[int, int] = (640, 480)
window: Surface = pygame.display.set_mode(DEFAULT_WINDOW_SIZE)
pygame.display.set_caption("English Battle")
zombies: list[Zombie] = []

level: Level
character: Hero

repeat: bool = True
# Para limitar los FPS
clock: Clock = pygame.time.Clock()

ZOMBIE_MOVE_INTERVAL: int = 10
zombie_move_counter: int = 0

attack_pressed: bool = False

combat_instance: Optional[Combat] = None
combat_input_text = ""
combat_result_text = ""
font = pygame.font.SysFont(FONT, 24)


def handle_events() -> None:
  """Handles all pygame events."""
  global repeat, combat_input_text, combat_result_text
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      repeat = False
    level.handle_combat_event(event, font)
    combat = level.get_combat_instance()
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

  combat_instance = level.get_combat_instance()
  if combat_instance is None or not combat_instance.get_active():
    character.move(dx, dy, moving, DEFAULT_WINDOW_SIZE[0],
                   DEFAULT_WINDOW_SIZE[1],
                   level=level, other_characters=zombies)
  # Si hay combate, nadie se mueve (ni héroe ni zombies)
  else:
    # Bloquea movimiento del héroe y zombies durante combate
    pass


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
        combat_instance is None or not combat_instance.get_active()):
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
      hero_center = (character.get_x() + 23 // 2, character.get_y() + 30 // 2)
      zombie_center = (zombie.get_x() + 23 // 2, zombie.get_y() + 30 // 2)
      dist = ((hero_center[0] - zombie_center[0]) ** 2 +
              (hero_center[1] - zombie_center[1]) ** 2) ** 0.5
      if dist <= character.get_attack_range() and dist < min_dist:
        target = zombie
        min_dist = dist
  return target


def _find_closest_zombie() -> Optional[Zombie]:
  """Finds the closest zombie (regardless of range)."""
  min_dist = float('inf')
  closest = None
  for zombie in zombies:
    if zombie.is_alive():
      hero_center = (character.get_x() + 23 // 2, character.get_y() + 30 // 2)
      zombie_center = (zombie.get_x() + 23 // 2, zombie.get_y() + 30 // 2)
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
    combat_instance = level.get_combat_instance()
    if combat_instance is None or not combat_instance.get_active():
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
  combat = level.get_combat_instance()
  combat_modal = level.get_combat_modal()
  if combat is not None and combat.get_active() and combat_modal:
    # El modal ya dibuja su propio fondo semitransparente y prompt
    combat_modal.draw(window)
  pygame.display.flip()


def update_all_sprites() -> None:
  """Updates all character sprites."""
  character.update_sprite_after_damage()
  for zombie in zombies:
    zombie.update_sprite_after_damage()


def draw_menu(menu_window: Surface, menu_font: FontType,
    background_img: Surface,
    selected_idx,
    options) -> None:
  """
  Draws main menu.
  """
  menu_window.blit(background_img, (0, 0))
  overlay = pygame.Surface(DEFAULT_WINDOW_SIZE)
  overlay.set_alpha(180)
  overlay.fill((0, 0, 0))
  menu_window.blit(overlay, (0, 0))
  title = menu_font.render("English Battle", True, (255, 255, 255))
  menu_window.blit(title,
                   (DEFAULT_WINDOW_SIZE[0] // 2 - title.get_width() // 2, 60))
  for idx, opt in enumerate(options):
    color = Color.MENU_SELECTED_BTN if idx == selected_idx else Color.MENU_UNSELECTED_BTN
    txt = menu_font.render(opt, True, color)
    x = DEFAULT_WINDOW_SIZE[0] // 2 - txt.get_width() // 2
    y = 160 + idx * 60
    menu_window.blit(txt, (x, y))
  pygame.display.flip()


def draw_level_select(win: Surface, menu_font: FontType,
    background_img: Surface,
    selected_idx: int,
    levels: dict[str, int]) -> None:
  """
  Draws level selection menu.
  """
  win.blit(background_img, (0, 0))
  overlay = pygame.Surface(DEFAULT_WINDOW_SIZE)
  overlay.set_alpha(180)
  overlay.fill((0, 0, 0))
  win.blit(overlay, (0, 0))
  title = menu_font.render("Selecciona nivel", True, (255, 255, 255))
  win.blit(title, (DEFAULT_WINDOW_SIZE[0] // 2 - title.get_width() // 2, 60))

  level_font = pygame.font.SysFont(FONT, 20)
  max_visible = 7
  half = max_visible // 2
  start_idx = max(0, selected_idx - half)
  end_idx = min(len(levels), start_idx + max_visible)
  if end_idx - start_idx < max_visible:
    start_idx = max(0, end_idx - max_visible)
  visible_levels = levels[start_idx:end_idx]

  for idx, lvl in enumerate(visible_levels):
    real_idx = start_idx + idx
    color = (0, 255, 0) if real_idx == selected_idx else (255, 255, 255)
    txt = level_font.render(lvl, True, color)
    x = DEFAULT_WINDOW_SIZE[0] // 2 - txt.get_width() // 2
    y = 160 + idx * 36
    win.blit(txt, (x, y))
  pygame.display.flip()


def get_level_type(type_str: str) -> LevelType:
  """Returns the LevelType enum from string."""
  if type_str == "multiple_choice":
    return LevelType.MULTIPLE_CHOICE
  elif type_str == "word_ordering":
    return LevelType.WORD_ORDERING
  elif type_str == "fill_in_the_blank":
    return LevelType.FILL_IN_THE_BLANK
  else:
    return LevelType.MULTIPLE_CHOICE


def level_select_menu(bg_img: Surface) -> Optional[int]:
  """Displays the level selection menu and handles navigation."""
  font_menu = pygame.font.SysFont(FONT, 32)
  levels = [lvl["name"] for lvl in LEVELS_CONFIG]
  levels.append("Volver")
  selected = 0
  level_selected = False
  channel: Channel = pygame.mixer.find_channel()
  while not level_selected:
    draw_level_select(window, font_menu, bg_img, selected, levels)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        close_game()
      elif event.type == pygame.KEYDOWN:
        channel.play(SOUNDS["blip1"])
        if event.key == pygame.K_UP or event.key == pygame.K_LEFT:
          selected = (selected - 1) % len(levels)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
          selected = (selected + 1) % len(levels)
        elif event.key == pygame.K_RETURN:
          level_selected = True
  if levels[selected] == "Volver":
    return None
  return selected


def setup_level(level_idx: int) -> None:
  """Initializes the level and characters according to selected config."""
  global character, level, zombies
  config = LEVELS_CONFIG[level_idx]
  character = Hero(50, 50, health=50)
  level = Level(window_size=DEFAULT_WINDOW_SIZE,
                difficulty=config["difficulty"],
                level_type=get_level_type(config["type"]),
                background_name=config["background"],
                wall_color=config["wall_color"])
  zombies = level.generate_zombies(config["num_zombies"])


def main_menu() -> None:
  """Displays the main menu and handles navigation."""
  font_menu = pygame.font.SysFont(FONT, 32)
  bg_img = pygame.transform.scale(random.choice(list(BACKGROUNDS.items()))[1],
                                  DEFAULT_WINDOW_SIZE)
  options = ["Nuevo juego", "Salir"]
  idx_selected = 0
  channel: Channel = pygame.mixer.find_channel()
  menu_active = True
  selected_level = False
  while menu_active:
    draw_menu(window, font_menu, bg_img, idx_selected, options)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        close_game()
      elif event.type == pygame.KEYDOWN:
        channel.play(SOUNDS["blip1"])
        if event.key == pygame.K_UP:
          idx_selected = (idx_selected - 1) % len(options)
        elif event.key == pygame.K_DOWN:
          idx_selected = (idx_selected + 1) % len(options)
        elif event.key == pygame.K_RETURN:
          if options[idx_selected] == "Nuevo juego":
            level_idx = level_select_menu(bg_img)
            if level_idx is None:
              selected_level = False
              continue
            setup_level(level_idx)
            selected_level = True
            menu_active = False
          elif options[idx_selected] == "Salir":
            close_game()
    if selected_level:
      menu_active = False


def close_game() -> None:
  """Closes the game."""
  pygame.quit()
  sys.exit()


def check_advance_level() -> None:
  """Checks if the hero crosses the open door and advances to the next level."""
  global level, character, zombies
  door: Door = level.get_door()
  if door and door.get_state() == "open":
    hero_rect = pygame.Rect(character.get_x(), character.get_y(), 23, 30)
    door_rect = pygame.Rect(door.get_x(), door.get_y(), 10, 14)
    if hero_rect.colliderect(door_rect):
      sound = SOUNDS.get("latchunlocked2")
      transition_black_screen()
      if sound:
        sound.play()
      next_level_idx = get_next_level_index()
      if next_level_idx is not None:
        setup_level(next_level_idx)
      else:
        # TODO: Pantalla de victoria
        main_menu()


def get_next_level_index() -> int | None:
  """Returns the index of the next level, or None if finished."""
  # No es confiable, mejor buscar por config
  current_idx = None
  for idx, lvl in enumerate(LEVELS_CONFIG):
    if lvl["difficulty"] == level.get_difficulty() and lvl[
      "type"] == level.get_level_type().value:
      current_idx = idx
      break
  if current_idx is not None and current_idx + 1 < len(LEVELS_CONFIG):
    return current_idx + 1
  return None


def transition_black_screen(duration: float = 1.0) -> None:
  """Shows a black screen for the given duration (seconds)."""
  window.fill((0, 0, 0))
  pygame.display.flip()
  pygame.time.delay(int(duration * 1000))


def main_loop() -> None:
  """Main game loop."""
  global repeat
  main_menu()
  while repeat:
    if not character.is_alive():
      level.play_death_sounds()
      transition_black_screen(3)
      main_menu()
      repeat = False
    handle_events()
    move_character()
    handle_combat_trigger()
    handle_attack()
    move_zombies()
    update_all_sprites()
    level.check_open_door(zombies)
    level.check_medkit_pickup(character)
    check_advance_level()
    draw_game()
    clock.tick(60)
  close_game()


if __name__ == "__main__":
  main_loop()
