"""Module for generating and managing maze levels in a game."""
import random
import time
from enum import Enum

import pygame
from pygame import Rect, Surface
from pygame.event import EventType
from pygame.font import FontType
from pygame.mixer import Channel

from Sound import SOUNDS
from Sprite.Backgrounds import BACKGROUNDS
from Sprite.Levels import DOOR_1_SPRITES, MEDKIT_SPRITES
from lib.Color import Color
from lib.Combat import Combat, WordOrderingModal, MultipleChoiceModal, \
  FillGapsModal
from lib.Objects import Door, Medkit
from lib.Var import Var


class LevelType(Enum):
  """Enumeration for different level types."""
  WORD_ORDERING = "word_ordering"
  FILL_IN_THE_BLANK = "fill_in_the_blank"
  MULTIPLE_CHOICE = "multiple_choice"


class Level:
  """Class to manage the game level, including background and maze."""

  def __init__(self,
      background_name: str,
      difficulty: int,
      level_type: LevelType,
      hero: 'Hero',
      window_size: tuple[int, int] = Var.DEFAULT_WINDOW_SIZE,
      wall_color: tuple[int, int, int] = Color.WALL_COLOR_DEFAULT) -> None:
    """
    Initializes the Level with maze, background, and questions.

    """
    self.__death_handled: None = None
    self.__window_size: tuple[int, int] = window_size
    self.__background_name: str = background_name
    self.__background: Surface = pygame.transform.scale(
        BACKGROUNDS[self.__background_name], self.__window_size
    )
    self.__maze_walls: list[Rect] = self._generate_random_maze(
        self.__window_size)
    self.__difficulty: int = difficulty
    self.__level_type: LevelType = level_type
    self.__questions_set = Var.QUESTIONS.get(self.__difficulty, {}).get(
        self.__level_type.value,
        [])
    self.__door = self._spawn_door()
    self.__medkits = self._spawn_medkits()
    self.__combat_instance: 'Combat | None' = None
    self.__combat_modal: 'BaseCombatModal | None' = None
    self.__wall_color = wall_color
    self.__hero = hero
    self.__pause_menu = None
    self.__pause_menu_font = pygame.font.SysFont(Var.FONT, 28)

  def get_level_type(self) -> LevelType:
    """Returns the level type."""
    return self.__level_type

  def get_difficulty(self) -> int:
    """Returns the difficulty level."""
    return self.__difficulty

  def get_character(self) -> 'Hero':
    """Returns the character associated with the level."""
    return self.__hero

  def _spawn_door(self) -> 'Door':
    """Spawns a door in a valid position (not colliding with maze walls)."""
    sprite_w, sprite_h = 40, 60
    max_attempts = 100
    for _ in range(max_attempts):
      x = random.randint(0, self.__window_size[0] - sprite_w)
      y = random.randint(0, self.__window_size[1] - sprite_h)
      rect = pygame.Rect(x, y, sprite_w, sprite_h)
      if not self.check_collision(rect):
        return Door(x, y, DOOR_1_SPRITES)
    # Si no encuentra lugar, la pone en (0,0)
    return Door(0, 0, DOOR_1_SPRITES)

  def _spawn_medkits(self) -> list['Medkit']:
    """Spawns medkits randomly, less likely as difficulty increases."""
    medkits = []
    sprite_w, sprite_h = 24, 24
    max_medkits = max(0, 2 - self.__difficulty)
    for _ in range(max_medkits):
      if random.random() < (1.0 - self.__difficulty * 0.15):
        for _ in range(50):
          x = random.randint(0, self.__window_size[0] - sprite_w)
          y = random.randint(0, self.__window_size[1] - sprite_h)
          rect = pygame.Rect(x, y, sprite_w, sprite_h)
          if not self.check_collision(rect):
            medkits.append(Medkit(x, y, MEDKIT_SPRITES))
            break
    return medkits

  def get_door(self) -> Door:
    """Returns the door object."""
    return self.__door

  @staticmethod
  def _init_maze_structures(cols: int, rows: int) -> tuple:
    """
    Initializes the structures for maze generation.
    """
    visited: list[list[bool]] = [[False for _ in range(rows)] for _ in
                                 range(cols)]
    vertical_walls: list[list[bool]] = [[True for _ in range(rows)] for _ in
                                        range(cols + 1)]
    horizontal_walls: list[list[bool]] = [[True for _ in range(rows + 1)] for _
                                          in range(cols)]
    return visited, vertical_walls, horizontal_walls

  def _dfs_maze(self, cx: int, cy: int, cols: int, rows: int,
      visited: list[list[bool]],
      vertical_walls: list[list[int]],
      horizontal_walls: list[list[int]]) -> None:
    """Depth-First Search maze generation algorithm."""
    visited[cx][cy] = True
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    random.shuffle(directions)
    for dx, dy in directions:
      nx, ny = cx + dx, cy + dy
      if 0 <= nx < cols and 0 <= ny < rows and not visited[nx][ny]:
        if dx == 1:  # right
          vertical_walls[cx + 1][cy] = False
        if dx == -1:  # left
          vertical_walls[cx][cy] = False
        if dy == 1:  # down
          horizontal_walls[cx][cy + 1] = False
        if dy == -1:  # up
          horizontal_walls[cx][cy] = False
        self._dfs_maze(nx, ny, cols, rows, visited, vertical_walls,
                       horizontal_walls)

  @staticmethod
  def _build_maze_walls(cols: int, rows: int, cell_size: int,
      wall_thickness: int,
      window_size: tuple[int, int],
      vertical_walls: list[list[int]], horizontal_walls: list[list[int]]) -> \
      list[Rect]:
    """Builds the maze walls from the wall structures."""
    w, h = window_size
    walls: list[Rect] = []
    # Build vertical walls
    for x in range(cols + 1):
      for y in range(rows):
        if vertical_walls[x][y]:
          wx = x * cell_size
          wy = y * cell_size
          walls.append(pygame.Rect(wx, wy, wall_thickness, cell_size))
    # Build horizontal walls
    for x in range(cols):
      for y in range(rows + 1):
        if horizontal_walls[x][y]:
          wx = x * cell_size
          wy = y * cell_size
          walls.append(pygame.Rect(wx, wy, cell_size, wall_thickness))
    # Maze borders
    walls.append(pygame.Rect(0, 0, w, wall_thickness))  # top
    walls.append(
        pygame.Rect(0, h - wall_thickness, w, wall_thickness))  # bottom
    walls.append(pygame.Rect(0, 0, wall_thickness, h))  # left
    walls.append(pygame.Rect(w - wall_thickness, 0, wall_thickness, h))  # right
    return walls

  def _generate_random_maze(self, window_size: tuple[int, int],
      wall_thickness: int = Var.DEFAULT_WALL_THICKNESS,
      cell_size: int = Var.DEFAULT_CELL_SIZE) -> list[Rect]:
    """
    Generates a random maze using DFS algorithm.
    """
    w, h = window_size
    cols = w // cell_size
    rows = h // cell_size

    visited, vertical_walls, horizontal_walls = self._init_maze_structures(cols,
                                                                           rows)
    start_x = random.randint(0, cols - 1)
    start_y = random.randint(0, rows - 1)
    self._dfs_maze(start_x, start_y, cols, rows, visited, vertical_walls,
                   horizontal_walls)
    walls = self._build_maze_walls(cols, rows, cell_size, wall_thickness,
                                   window_size,
                                   vertical_walls, horizontal_walls)
    return walls

  def draw_background(self, surface: Surface) -> None:
    """Draws the background image on the given surface."""
    surface.blit(self.__background, (0, 0))

  def draw_maze(self, surface: Surface) -> None:
    """Draws the maze walls and the door on the given surface."""
    for wall in self.__maze_walls:
      pygame.draw.rect(surface, self.__wall_color, wall)
    if self.__door:
      if self.__door.get_state() == "opening":
        self.__door.animate_opening()
      self.__door.draw(surface)
    for medkit in self.__medkits:
      if not medkit.get_used():
        medkit.draw(surface)

  def check_collision(self, rect: Rect) -> bool:
    """Returns True if rect collides with any maze wall."""
    for wall in self.__maze_walls:
      if rect.colliderect(wall):
        return True
    return False

  @staticmethod
  def play_death_sounds() -> None:
    """
    Plays beep sound twice and then flatline, each after the previous finishes.
    """
    channel: Channel = pygame.mixer.find_channel()
    if channel is None:
      return
    channel.set_endevent(pygame.USEREVENT + 1)
    sounds = [SOUNDS["beep"], SOUNDS["beep"], SOUNDS["flatline"]]
    for s in sounds:
      channel.queue(s)
    channel.set_volume(0.5)
    channel.get_queue().play(fade_ms=7000)

  def generate_zombies(self, num_zombies: int) -> list['Zombie']:
    """Generates zombies at random positions not colliding with walls."""
    from lib.Core import Zombie
    zombies: list[Zombie] = []
    sprite_w, sprite_h = (23, 30)
    x: int = 0
    y: int = 0
    for _ in range(num_zombies):
      valid_spawn = False
      while not valid_spawn:
        x = random.randint(0, self.__window_size[0] - sprite_w)
        y = random.randint(0, self.__window_size[1] - sprite_h)
        rect = pygame.Rect(x, y, sprite_w, sprite_h)
        if not self.check_collision(rect):
          valid_spawn = True
      health = 10 + (self.__difficulty - 1) * 5
      zombies.append(Zombie(x, y, health=health))
    return zombies

  def start_combat(self, character: 'Character', zombies: list['Zombie'],
      font: FontType) -> bool:
    """Starts combat if the hero is near a zombie."""
    if self.__combat_instance is None or not self.__combat_instance.get_active():
      for zombie in zombies:
        if zombie.is_alive() and character.can_attack(zombie):
          self.__combat_instance = Combat(character, zombie,
                                          self.__level_type.value,
                                          self.__questions_set)
          question = self.__combat_instance.generate_question()
          if self.__level_type == LevelType.WORD_ORDERING:
            words = question.split(" / ")
            self.__combat_modal = WordOrderingModal(words, font,
                                                    pygame.Rect(40, 100, 560,
                                                                260))
          elif self.__level_type == LevelType.MULTIPLE_CHOICE:
            q, options, _ = self.__combat_instance.get_current_question()
            self.__combat_modal = MultipleChoiceModal(q, options, font,
                                                      pygame.Rect(40, 100, 560,
                                                                  260))
          elif self.__level_type == LevelType.FILL_IN_THE_BLANK:
            self.__combat_modal = FillGapsModal(question, font,
                                                pygame.Rect(40, 100, 560, 260))
          else:
            self.__combat_modal = None
          return True
    return False

  def handle_combat_event(self, event: EventType, font: FontType) -> None:
    """Handles events for combat and the modal."""
    if self.__combat_instance is not None and self.__combat_instance.get_active() and self.__combat_modal:
      self.__combat_modal.handle_combat_event(event)
      if self.__combat_modal.get_confirmed():
        player_answer = self.__combat_modal.get_player_answer()
        if player_answer:
          result = self.__combat_instance.process_turn(player_answer.strip())
          self.__combat_modal.set_result_text(result)
          FeedbackBox.get_instance().set_message(result, 3, 0)
          if self.__combat_instance.get_active():

            if self.__combat_instance.get_combat_type() == "word_ordering":
              words = self.__combat_instance.get_current_question().split(" / ")
              self.__combat_modal = WordOrderingModal(words, font,
                                                      pygame.Rect(40, 100, 560,
                                                                  260),
                                                      result_text=result)
            elif self.__combat_instance.get_combat_type() == "multiple_choice":
              q, options, _ = self.__combat_instance.get_current_question()
              self.__combat_modal = MultipleChoiceModal(q, options, font,
                                                        pygame.Rect(40, 100,
                                                                    560,
                                                                    260),
                                                        result_text=result)
            elif self.__combat_instance.get_combat_type() == "fill_in_the_blank":
              self.__combat_modal = FillGapsModal(
                  self.__combat_instance.get_current_question(), font,
                  pygame.Rect(40, 100, 560, 260), result_text=result)
            else:
              self.__combat_modal = None
          else:
            self.__combat_modal = None
        else:
          self.__combat_modal.set_confirmed(False)

  def get_combat_modal(self) -> 'BaseCombatModal':
    """Returns the current modal if it exists."""
    return self.__combat_modal

  def get_combat_instance(self) -> 'Combat':
    """Returns the current combat instance."""
    return self.__combat_instance

  def check_open_door(self, zombies: list['Zombie']) -> None:
    """Opens the door if all zombies are defeated."""
    if self.__door and self.__door.get_state() == "closed":
      if all(not z.is_alive() for z in zombies):
        self.__door.open()

  def check_medkit_pickup(self) -> None:
    """Checks if hero picks up a medkit and heals."""
    for medkit in self.__medkits:
      if not medkit.get_used() and self.__hero.get_health() < self.__hero.get_max_health():
        hero_rect = pygame.Rect(self.__hero.get_x(), self.__hero.get_y(), 23,
                                30)
        medkit_rect = pygame.Rect(medkit.get_x(), medkit.get_y(),
                                  24,
                                  24)
        if hero_rect.colliderect(medkit_rect):
          medkit.apply(self.__hero)

  def get_pause_menu(self):
    if self.__pause_menu is None:
      self.__pause_menu = PauseMenu(self.__pause_menu_font,
                                    pygame.Rect(120, 100, 400, 220))
    return self.__pause_menu

  def handle_pause_event(self, event: EventType) -> str | None:
    """
    Maneja eventos para el menú de pausa.
    """
    pause_menu = self.get_pause_menu()
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
      if not pause_menu.get_active():
        pause_menu.open()
        pygame.mixer.find_channel().play(SOUNDS["ui_click"])
        return "pause_opened"
      else:
        pause_menu.close()
        pygame.mixer.find_channel().play(SOUNDS["ui_clickrelease"])
        return "pause_closed"
    result = pause_menu.handle_event(event)
    if self.__pause_menu and self.__pause_menu.get_active() and event.type == pygame.KEYDOWN:
      if not pause_menu.get_confirming() and event.key in [pygame.K_UP,
                                                           pygame.K_DOWN]:
        pygame.mixer.find_channel().play(SOUNDS["blip1"])
      elif pause_menu.get_confirming() and event.key in [pygame.K_LEFT,
                                                         pygame.K_RIGHT]:
        pygame.mixer.find_channel().play(SOUNDS["blip1"])
    return result

  def draw_pause_menu(self, surface: Surface):
    pause_menu = self.get_pause_menu()
    if pause_menu.get_active():
      pause_menu.draw(surface)


class FeedbackBox:
  """Singleton class to show feedback messages on the screen with auto-hide."""

  __instance = None

  def __init__(self, font: str = Var.FONT, width: int = 160, height: int = 24,
      margin: int = 12) -> None:
    """
    Initializes the FeedbackBox singleton.
    """
    if FeedbackBox.__instance is not None:
      raise Exception(
          "Use FeedbackBox.get_instance() to get the singleton instance.")
    self.__message = ""
    self.__font = pygame.font.SysFont(font, 16)
    self.__width = width
    self.__height = height
    self.__margin = margin
    self.__duration = 5.0
    self.__start_time = None
    self.__delay = 0.0
    self.__delay_start_time = None
    FeedbackBox.__instance = self

  @staticmethod
  def get_instance() -> 'FeedbackBox':
    """
    Returns the singleton instance of FeedbackBox, creating it if necessary.
    """
    if FeedbackBox.__instance is None:
      FeedbackBox()
    return FeedbackBox.__instance

  @staticmethod
  def set_message(msg: str, duration: float = 5.0, delay: float = 0.0) -> None:
    """
    Sets the feedback message globally, with optional delay before showing.
    """
    box = FeedbackBox.get_instance()
    box._set_message(msg, duration, delay)

  def _set_message(self, msg: str, duration: float = 5.0,
      delay: float = 0.0) -> None:
    if msg != self.__message:
      print("Setting new message:", msg)
      self.__message = msg
      self.__duration = duration
      self.__delay = delay
      self.__delay_start_time = time.time() if delay > 0 else None
      self.__start_time = None if delay > 0 else time.time()

  def get_message(self) -> str:
    """
    Returns the current feedback message.
    """
    return self.__message

  def _clear(self) -> None:
    """
    Clears the feedback message immediately.
    """
    self.__message = ""
    self.__start_time = None

  def _wrap_text(self, text: str) -> list[str]:
    """
    Divides the text into lines that fit within the box width.
    """
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
      test_line = current_line + (" " if current_line else "") + word
      test_surface = self.__font.render(test_line, True, Var.TEXT_COLOR)
      if test_surface.get_width() <= self.__width - 32:
        current_line = test_line
      else:
        if current_line:
          lines.append(current_line)
        current_line = word
    if current_line:
      lines.append(current_line)
    return lines

  def draw(self, surface: pygame.Surface) -> None:
    """
    Draws the feedback box on the given surface if time not expired and delay passed.
    """
    if self.__message:
      if self.__delay > 0 and self.__delay_start_time is not None:
        elapsed_delay = time.time() - self.__delay_start_time
        if elapsed_delay > self.__delay:
          self.__start_time = time.time()
          self.__delay = 0
          self.__delay_start_time = None
          pygame.mixer.find_channel().play(SOUNDS["ui_rollover"])
      if self.__start_time is not None:
        elapsed = time.time() - self.__start_time
        lines = self._wrap_text(self.__message)
        line_height = self.__font.get_height()
        box_height = max(self.__height, line_height * len(lines) + 18)
        box = pygame.Surface((self.__width, box_height), pygame.SRCALPHA)
        box.fill(Color.FEEDBACK_BG)
        surface.blit(box, (self.__margin, self.__margin))
        for i, line in enumerate(lines):
          txt = self.__font.render(line, True, Var.TEXT_COLOR)
          surface.blit(txt, (self.__margin + 16,
                             self.__margin + 9 + i * line_height))
        if elapsed > self.__duration:
          self._clear()


class PauseMenu:
  """Pause menu class"""

  def __init__(self, font: FontType, rect: Rect) -> None:
    self.__font = font
    self.__rect = rect
    self.__selected = 0
    self.__confirming = False
    self.__confirm_selected = 1
    self.__active = False

    self.__btn_rects = [
      pygame.Rect(rect.x + 40, rect.y + 60, rect.width - 80, 40),
      pygame.Rect(rect.x + 40, rect.y + 120, rect.width - 80, 40)
    ]
    self.__confirm_rects = [
      pygame.Rect(rect.x + 60, rect.y + 120, 80, 40),
      pygame.Rect(rect.x + rect.width - 140, rect.y + 120, 80, 40)
    ]

  def get_confirming(self) -> bool:
    return self.__confirming

  def get_active(self) -> bool:
    return self.__active

  def open(self):
    self.__active = True
    self.__selected = 0
    self.__confirming = False

  def close(self):
    self.__active = False
    self.__confirming = False

  def draw(self, surface: Surface):
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))
    pygame.draw.rect(surface, Color.MODAL_BG, self.__rect, border_radius=12)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.__rect, 2,
                     border_radius=12)
    title = self.__font.render("Menú de pausa", True, Color.TITLE_TEXT)
    surface.blit(title, (self.__rect.x + 20, self.__rect.y + 18))

    if not self.__confirming:
      for i, txt in enumerate(["Continuar", "Volver al menú principal"]):
        bg = Color.MENU_SELECTED_BTN if self.__selected == i else Color.MENU_UNSELECTED_BTN
        pygame.draw.rect(surface, bg, self.__btn_rects[i], border_radius=8)
        pygame.draw.rect(surface, Color.WORD_BORDER, self.__btn_rects[i], 2,
                         border_radius=8)
        txt_surf = self.__font.render(txt, True, Color.TITLE_TEXT)
        txt_rect = txt_surf.get_rect(center=self.__btn_rects[i].center)
        surface.blit(txt_surf, txt_rect)
    else:
      question = self.__font.render("¿Estás seguro?", True, Color.TITLE_TEXT)
      surface.blit(question, (self.__rect.x + 20, self.__rect.y + 70))
      for i, txt in enumerate(["Sí", "No"]):
        bg = Color.MENU_SELECTED_BTN if self.__confirm_selected == i else Color.MENU_UNSELECTED_BTN
        pygame.draw.rect(surface, bg, self.__confirm_rects[i], border_radius=8)
        pygame.draw.rect(surface, Color.WORD_BORDER, self.__confirm_rects[i], 2,
                         border_radius=8)
        txt_surf = self.__font.render(txt, True, Color.TITLE_TEXT)
        txt_rect = txt_surf.get_rect(center=self.__confirm_rects[i].center)
        surface.blit(txt_surf, txt_rect)

  def handle_event(self, event: EventType):
    if not self.__active:
      return None
    if event.type == pygame.KEYDOWN:
      if not self.__confirming:
        if event.key in [pygame.K_UP]:
          self.__selected = (self.__selected - 1) % 2
        elif event.key in [pygame.K_DOWN]:
          self.__selected = (self.__selected + 1) % 2
        elif event.key in [pygame.K_RETURN]:
          if self.__selected == 0:
            self.close()
            return "continue"
          elif self.__selected == 1:
            self.__confirming = True
            self.__confirm_selected = 1
      else:
        if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
          self.__confirm_selected = 1 if self.__confirm_selected == 0 else 0
          print("confirm selected set to", self.__confirm_selected)
        elif event.key in [pygame.K_RETURN]:
          print("confirm selected is", self.__confirm_selected)
          if self.__confirm_selected == 0:
            self.close()
            return "main_menu"
          else:
            self.__confirming = False
    return None


class TutorialLevel(Level):
  """Base class for tutorial levels."""

  def __init__(self, config: dict, hero: 'Hero') -> None:
    super().__init__(
        background_name=config.get("background", "grass"),
        difficulty=config.get("difficulty", 0),
        level_type=LevelType[config.get("type").upper()] if config.get(
            "type") and config.get(
            "type") != "none" else LevelType.MULTIPLE_CHOICE,
        window_size=Var.DEFAULT_WINDOW_SIZE,
        wall_color=config.get("wall_color", Color.WALL_COLOR_GRASS),
        hero=hero
    )
    self.__tutorial_config = config
    self._show_message()

  def _show_message(self) -> None:
    msg = self.__tutorial_config.get("message")
    if msg:
      FeedbackBox.get_instance().set_message(msg, 8, 1.5)

  def _generate_random_maze(self, window_size: tuple[int, int],
      wall_thickness: int = Var.DEFAULT_WALL_THICKNESS,
      cell_size: int = Var.DEFAULT_CELL_SIZE) -> list[Rect]:
    return []

  def _spawn_door(self) -> 'Door':
    # Puerta en posición fija para tutorial
    sprite_w, sprite_h = 40, 60
    x = Var.DEFAULT_WINDOW_SIZE[0] - sprite_w - 30
    y = Var.DEFAULT_WINDOW_SIZE[1] // 2 - sprite_h // 2
    return Door(x, y, DOOR_1_SPRITES)

  def _spawn_medkits(self) -> list['Medkit']:
    return []

  def generate_zombies(self, num_zombies: int) -> list['Zombie']:
    return []


class TutorialMoveLevel(TutorialLevel):
  """Movement tutorial."""

  def __init__(self, config: dict, hero: 'Hero') -> None:
    super().__init__(config, hero)
    self._show_message()


class TutorialCombatLevel(TutorialLevel):
  """Combat tutorial"""

  def __init__(self, config: dict, hero: 'Hero') -> None:
    super().__init__(config, hero)
    self._show_message()

  def generate_zombies(self, num_zombies: int):
    """One zombie in fixed position for combat tutorial."""
    from lib.Core import Zombie
    sprite_w, sprite_h = (23, 30)
    x = Var.DEFAULT_WINDOW_SIZE[0] // 2 - sprite_w // 2
    y = Var.DEFAULT_WINDOW_SIZE[1] // 2 - sprite_h // 2
    return [Zombie(x, y, health=10)]


class TutorialHealLevel(TutorialLevel):
  """Healing tutorial."""

  def __init__(self, config: dict, hero: 'Hero') -> None:
    super().__init__(config, hero)
    self._show_message()
    self.get_character().receive_damage(25)

  def _spawn_medkits(self) -> list['Medkit']:
    sprite_w, sprite_h = 24, 24
    x = Var.DEFAULT_WINDOW_SIZE[0] // 2 - sprite_w // 2
    y = Var.DEFAULT_WINDOW_SIZE[1] // 2 - sprite_h // 2
    return [Medkit(x, y, MEDKIT_SPRITES)]
