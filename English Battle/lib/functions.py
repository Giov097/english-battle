"""Functions"""
import random
import sys
from typing import Optional

import pygame
from pygame import Surface
from pygame.font import Font
from pygame.mixer import Channel

from font import FONTS
from lib.color import Color
from lib.core import Zombie, Hero
from lib.level import (Level, TutorialLevel, TutorialCombatLevel,
                       TutorialMoveLevel, TutorialHealLevel, LevelType,
                       FeedbackBox)
from lib.objects import Door
from lib.var import Var
from sound import SOUNDS, MUSIC
from sprite.backgrounds import BACKGROUNDS


def create_level_from_config(config: dict, hero: 'Hero') -> Level:
  """
  Creates a Level or TutorialLevel based on the config dictionary.
  :param config: Configuration dictionary for the level.
  :param hero: The hero character for the level.
  :return: An instance of Level or TutorialLevel.
  """
  level: Level
  if config.get("tutorial"):
    step = config.get("tutorial_step")
    if step == "move":
      level = TutorialMoveLevel(config, hero)
    elif step == "combat":
      level = TutorialCombatLevel(config, hero)
    elif step == "heal":
      level = TutorialHealLevel(config, hero)
    else:
      level = TutorialLevel(config, hero)
  else:
    level = Level(
        background_name=config.get("background", "grass"),
        difficulty=config.get("difficulty", 1),
        level_type=LevelType[config.get("type").upper()],
        window_size=Var.DEFAULT_WINDOW_SIZE,
        wall_color=config.get("wall_color", Color.WALL_COLOR_GRASS),
        hero=hero)
  return level


def transition_black_screen(window: Surface, duration: float = 1.0) -> None:
  """
  Shows a black screen for the given duration (seconds).
  :param window: The Pygame window surface.
  :param duration: Duration in seconds to show the black screen.
  """
  window.fill(Color.TRANSITION_SCREEN)
  pygame.display.flip()
  pygame.time.delay(int(duration * 1000))


def get_next_level_index(current_level_idx: int) -> int | None:
  """
  Returns the index of the next level, or None if finished.
  :param current_level_idx: The current level index.
  :return: The next level index or None if there are no more levels.
  """
  if current_level_idx is not None and current_level_idx + 1 < len(
      Var.LEVELS_CONFIG):
    return current_level_idx + 1
  return None


def close_game() -> None:
  """Closes the game."""
  pygame.quit()
  sys.exit()


def find_attackable_zombie(hero: Hero, zombies: list[Zombie]) -> Optional[
  Zombie]:
  """
  Finds the closest zombie within attack range.
  :param hero: The hero character.
  :param zombies: List of zombies to check.
  :return: The closest attackable zombie or None if none are in range.
  """
  min_dist = float('inf')
  target = None
  for zombie in zombies:
    if zombie.is_alive():
      hero_center = (hero.get_x() + 23 // 2, hero.get_y() + 30 // 2)
      zombie_center = (zombie.get_x() + 23 // 2, zombie.get_y() + 30 // 2)
      dist = ((hero_center[0] - zombie_center[0]) ** 2 +
              (hero_center[1] - zombie_center[1]) ** 2) ** 0.5
      if dist <= hero.get_attack_range() and dist < min_dist:
        target = zombie
        min_dist = dist
  return target


def find_closest_zombie(hero: Hero, zombies: list[Zombie]) -> Optional[
  Zombie]:
  """
  Finds the closest zombie (regardless of range).
  :param hero: The hero character.
  :param zombies: List of zombies to check.
  :return: The closest zombie or None if no zombies are alive.
  """
  min_dist = float('inf')
  closest = None
  for zombie in zombies:
    if zombie.is_alive():
      hero_center = (hero.get_x() + 23 // 2, hero.get_y() + 30 // 2)
      zombie_center = (zombie.get_x() + 23 // 2, zombie.get_y() + 30 // 2)
      dist = ((hero_center[0] - zombie_center[0]) ** 2 +
              (hero_center[1] - zombie_center[1]) ** 2) ** 0.5
      if dist < min_dist:
        closest = zombie
        min_dist = dist
  return closest


def draw_game(lvl: Level, window: Surface, hero: Hero,
    zombies: list[Zombie]) -> None:
  """
  Draws all game elements on the window.
  :param lvl: The current game level.
  :param window: The Pygame window surface.
  :param hero: The hero character.
  :param zombies: List of zombies in the level.
  """
  lvl.draw_background(window)
  lvl.draw_maze(window)
  for zombie in zombies:
    if not zombie.is_alive():
      zombie.draw(window)
  hero.draw(window)
  for zombie in zombies:
    if zombie.is_alive():
      zombie.draw(window)

  combat = lvl.get_combat_instance()
  combat_modal = lvl.get_combat_modal()
  if combat is not None and combat.get_active() and combat_modal:
    combat_modal.draw(window)
  FeedbackBox.get_instance().draw(window)
  lvl.draw_pause_menu(window)
  pygame.display.flip()


def check_advance_level(lvl: Level, hero: Hero, window: Surface) -> None:
  """
  Checks if the hero crosses the open door and advances to the next level.
  :param lvl: Current game level.
  :param hero: The hero character.
  :param window: The Pygame window surface.
  """
  door: Door = lvl.get_door()
  if door and door.get_state() == "open":
    hero_rect = pygame.Rect(hero.get_x(), hero.get_y(), 23, 30)
    door_rect = pygame.Rect(door.get_x(), door.get_y(), 10, 14)
    if hero_rect.colliderect(door_rect):
      sound = SOUNDS.get("latchunlocked2")
      transition_black_screen(window)
      if sound:
        sound.play()
      next_level_idx = get_next_level_index(Var.current_level_idx)
      if next_level_idx is not None:
        Var.current_level_idx = next_level_idx
        Var.character, Var.level, Var.zombies = setup_level(next_level_idx)
      else:
        # TODO: Pantalla de victoria
        main_menu(window)


def main_menu(window: Surface) -> None:
  """
  Displays the main menu and handles navigation.
  :param window: The pygame window surface.
  """
  font_title = pygame.font.Font(FONTS.get("retro-british"), 32)
  font_menu = pygame.font.Font(FONTS.get("press-start-2p"), 16)
  bg_img = pygame.transform.scale(random.choice(list(BACKGROUNDS.items()))[1],
                                  Var.DEFAULT_WINDOW_SIZE)
  options = ["Nuevo juego", "Salir"]
  idx_selected = 0
  channel: Channel = Var.SFX_CHANNEL
  menu_active = True
  selected_level = False
  while menu_active:
    draw_menu(window, font_title, font_menu, bg_img, idx_selected, options)
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
            Var.current_level_idx = level_select_menu(window, bg_img)
            if Var.current_level_idx is None:
              selected_level = False
              continue
            Var.character, Var.level, Var.zombies = setup_level(
                Var.current_level_idx)
            selected_level = True
            menu_active = False
          elif options[idx_selected] == "Salir":
            close_game()
    if selected_level:
      menu_active = False


def setup_level(level_idx: int) -> tuple[Hero, Level, list[Zombie]]:
  """
  Initializes the level and characters according to selected config.
  :param level_idx: Index of the level to set up.
  :return: Tuple of (character, level, zombies).
  """
  print("Initializing level:", Var.LEVELS_CONFIG[level_idx]["name"])
  config = Var.LEVELS_CONFIG[level_idx]
  character = Hero(50, 100, health=50)
  if config.get("tutorial"):
    level = create_level_from_config(config,
                                     hero=character)
  else:
    level = Level(window_size=Var.DEFAULT_WINDOW_SIZE,
                  difficulty=config["difficulty"],
                  level_type=get_level_type(config["type"]),
                  background_name=config["background"],
                  wall_color=config["wall_color"],
                  hero=character)
  zombies = level.generate_zombies(config["num_zombies"])
  if not ("tutorial" in config and config["tutorial"]) and Var.first_level:
    FeedbackBox.get_instance().set_message(
        "¡Bienvenido! Derrota a todos los zombis para avanzar", 3, 2)
    Var.first_level = False
  return character, level, zombies


def draw_menu(menu_window: Surface, menu_font: Font, title_font: Font,
    background_img: Surface,
    selected_idx: int,
    options) -> None:
  """
  Draws main menu.
  :param menu_window: The pygame window surface.
  :param title_font: font for the title.
  :param menu_font: font for the menu options.
  :param background_img: Background image for the menu.
  :param selected_idx: Index of the currently selected option.
  :param options: List of menu option strings.
  """
  menu_window.blit(background_img, (0, 0))
  overlay = pygame.Surface(Var.DEFAULT_WINDOW_SIZE)
  overlay.set_alpha(180)
  overlay.fill((0, 0, 0))
  menu_window.blit(overlay, (0, 0))
  title = menu_font.render("English Battle", True, Color.TEXT)
  menu_window.blit(title,
                   (Var.DEFAULT_WINDOW_SIZE[0] // 2 - title.get_width() // 2,
                    60))
  for idx, opt in enumerate(options):
    color = Color.MENU_SELECTED_BTN if idx == selected_idx else Color.MENU_UNSELECTED_BTN
    txt = title_font.render(opt, True, color)
    x = Var.DEFAULT_WINDOW_SIZE[0] // 2 - txt.get_width() // 2
    y = 160 + idx * 60
    menu_window.blit(txt, (x, y))
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


def level_select_menu(window: Surface, bg_img: Surface) -> Optional[int]:
  """Displays the level selection menu and handles navigation."""
  levels = [lvl["name"] for lvl in Var.LEVELS_CONFIG]
  levels.append("Volver")
  selected = 0
  level_selected = False
  channel: Channel = Var.SFX_CHANNEL
  while not level_selected:
    draw_level_select(window, bg_img, selected, levels)
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


def draw_level_select(win: Surface,
    background_img: Surface,
    selected_idx: int,
    levels: dict[str, int]) -> None:
  """
  Draws level selection menu.
  :param win: The pygame window surface.
  :param background_img: Background image for the menu.
  :param selected_idx: Index of the currently selected level.
  :param levels: List of level names.
  """
  win.blit(background_img, (0, 0))
  overlay = pygame.Surface(Var.DEFAULT_WINDOW_SIZE)
  overlay.set_alpha(180)
  overlay.fill((0, 0, 0))
  win.blit(overlay, (0, 0))
  title_font = pygame.font.Font(FONTS.get("press-start-2p"), 20)
  level_font = pygame.font.Font(FONTS.get("press-start-2p"), 10)
  title = title_font.render("Selecciona nivel", True, Color.TEXT)
  win.blit(title,
           (Var.DEFAULT_WINDOW_SIZE[0] // 2 - title.get_width() // 2, 60))

  max_visible = 7
  half = max_visible // 2
  start_idx = max(0, selected_idx - half)
  end_idx = min(len(levels), start_idx + max_visible)
  if end_idx - start_idx < max_visible:
    start_idx = max(0, end_idx - max_visible)
  visible_levels = levels[start_idx:end_idx]

  for idx, lvl in enumerate(visible_levels):
    real_idx = start_idx + idx
    color = Color.HIGHLIGHT_TEXT if real_idx == selected_idx else Color.TEXT
    txt = level_font.render(lvl, True, color)
    x = Var.DEFAULT_WINDOW_SIZE[0] // 2 - txt.get_width() // 2
    y = 160 + idx * 36
    win.blit(txt, (x, y))
  pygame.display.flip()


def play_music() -> None:
  """
  Plays background music in a loop.
  """
  pygame.mixer.music.load(MUSIC.get("game-8-bit"))
  pygame.mixer.music.play(-1)


def update_all_sprites(character: Hero, zombies: list[Zombie]) -> None:
  """
  Updates all character sprites.
  :param character: The hero character.
  :param zombies: List of zombie characters.
  """
  character.update_sprite_after_damage()
  for zombie in zombies:
    zombie.update_sprite_after_damage()
