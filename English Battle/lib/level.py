"""Module for generating and managing maze levels in a game."""
import random
import time
from enum import Enum

import pygame
from pygame import Rect, Surface
from pygame.event import EventType
from pygame.font import FontType
from pygame.mixer import Channel

from font import FONTS
from sound import SOUNDS
from sprite.backgrounds import BACKGROUNDS
from sprite.levels import DOOR_1_SPRITES, MEDKIT_SPRITES
from lib.color import Color
from lib.combat import Combat, WordOrderingModal, MultipleChoiceModal, \
  FillGapsModal
from lib.objects import Door, Medkit
from lib.var import Var


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
      hero: 'hero',
      window_size: tuple[int, int] = Var.DEFAULT_WINDOW_SIZE,
      wall_color: tuple[int, int, int] = Color.WALL_COLOR_DEFAULT) -> None:
    """
    Initializes the Level with maze, background, and questions.
    :param background_name: Name of the background image.
    :param difficulty: Difficulty level (0-5).
    :param level_type: Type of questions for combat.
    :param hero: The hero character.
    :param window_size: Size of the game window.
    :param wall_color: Color of the maze walls.
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
    self.__pause_menu_font = pygame.font.Font(FONTS.get("press-start-2p"), 12)

  def get_level_type(self) -> LevelType:
    """
    Returns the level type.
    :return: LevelType enum value.
    """
    return self.__level_type

  def get_difficulty(self) -> int:
    """
    Returns the difficulty level.
    :return: Difficulty as an integer.
    """
    return self.__difficulty

  def get_hero(self) -> 'Hero':
    """
    Returns the character associated with the level.
    :return: hero object.
    """
    return self.__hero

  def _spawn_door(self) -> 'Door':
    """
    Spawns a door in a valid position.
    :return: door object.
    """
    sprite_w, sprite_h = 40, 60
    max_attempts = 100
    for _ in range(max_attempts):
      x = random.randint(0, self.__window_size[0] - sprite_w)
      y = random.randint(0, self.__window_size[1] - sprite_h)
      rect = pygame.Rect(x, y, sprite_w, sprite_h)
      if not self.check_collision(rect):
        return Door(x, y, DOOR_1_SPRITES)
    return Door(0, 0, DOOR_1_SPRITES)

  def _spawn_medkits(self) -> list['Medkit']:
    """
    Spawns medkits randomly, less likely as difficulty increases.
    :return: List of medkit objects.
    """
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
    """
    Returns the door object.
    :return: door object.
    """
    return self.__door

  @staticmethod
  def _init_maze_structures(cols: int, rows: int) -> tuple:
    """
    Initializes the structures for maze generation.
    :param cols: Number of columns in the maze.
    :param rows: Number of rows in the maze.
    :return: Tuple of visited cells, vertical walls, and horizontal walls.
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
    """
    Depth-First Search maze generation algorithm.
    :param cx: Current x position in the maze grid.
    :param cy: Current y position in the maze grid.
    :param cols: Total columns in the maze.
    :param rows: Total rows in the maze.
    :param visited: 2D list tracking visited cells.
    :param vertical_walls: 2D list tracking vertical walls.
    :param horizontal_walls: 2D list tracking horizontal walls.
    :return: None
    """
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
    """
    Builds the maze walls from the wall structures.
    :param cols: Number of columns in the maze.
    :param rows: Number of rows in the maze.
    :param cell_size: Size of each cell in pixels.
    :param wall_thickness: Thickness of the walls in pixels.
    :param window_size: Size of the game window.
    :param vertical_walls: 2D list of vertical wall presence.
    :param horizontal_walls: 2D list of horizontal wall presence.
    :return: List of Rect objects representing walls.
    """
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
    :param window_size: Size of the game window.
    :param wall_thickness: Thickness of the walls in pixels.
    :param cell_size: Size of each cell in pixels.
    :return: List of Rect objects representing maze walls.
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
    """
    Draws the background image on the given surface.
    :param surface: Pygame Surface to draw the background on.
    """
    surface.blit(self.__background, (0, 0))

  def draw_maze(self, surface: Surface) -> None:
    """
    Draws the maze walls and the door on the given surface.
    :param surface: Pygame Surface to draw the maze on.
    """
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
    """
    Returns True if rect collides with any maze wall.
    :param rect: Pygame Rect to check for collisions.
    """
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
    """
    Generates zombies at random positions not colliding with walls.
    :param num_zombies: Number of zombies to generate.
    :return: List of zombie objects.
    """
    from lib.core import Zombie
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
    """
    Starts combat if the hero is near a zombie.
    :param character: The hero character.
    :param zombies: List of zombies in the level.
    :param font: font to use for the combat modal.
    :return: True if combat started, False otherwise.
    """
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
    """
    Handles events for combat and the modal.
    :param event: Pygame event to handle.
    :param font: font to use for the combat modal.
    """
    if (
        self.__combat_instance is not None
        and self.__combat_instance.get_active()
        and self.__combat_modal
    ):
      self.__combat_modal.handle_combat_event(event)
      if self.__combat_modal.get_confirmed():
        player_answer = self.__combat_modal.get_player_answer()
        if player_answer:
          self._process_combat_answer(player_answer, font)
        else:
          self.__combat_modal.set_confirmed(False)

  def _process_combat_answer(self, player_answer: str, font: FontType) -> None:
    """
    Processes the player's answer in combat and updates the modal.
    :param player_answer: The answer provided by the player.
    :param font: font to use for the combat modal.
    """
    result = self.__combat_instance.process_turn(player_answer.strip())
    self.__combat_modal.set_result_text(result)
    FeedbackBox.get_instance().set_message(result, 3, 0)
    if self.__combat_instance.get_active():
      combat_type = self.__combat_instance.get_combat_type()
      if combat_type == "word_ordering":
        words = self.__combat_instance.get_current_question().split(" / ")
        self.__combat_modal = WordOrderingModal(
            words, font, pygame.Rect(40, 100, 560, 260), result_text=result
        )
      elif combat_type == "multiple_choice":
        q, options, _ = self.__combat_instance.get_current_question()
        self.__combat_modal = MultipleChoiceModal(
            q, options, font, pygame.Rect(40, 100, 560, 260), result_text=result
        )
      elif combat_type == "fill_in_the_blank":
        self.__combat_modal = FillGapsModal(
            self.__combat_instance.get_current_question(),
            font,
            pygame.Rect(40, 100, 560, 260),
            result_text=result,
        )
      else:
        self.__combat_modal = None
    else:
      self.__combat_modal = None

  def get_combat_modal(self) -> 'BaseCombatModal':
    """
    Returns the current modal if it exists.
    :return: Combat modal object.
    """
    return self.__combat_modal

  def get_combat_instance(self) -> 'Combat':
    """
    Returns the current combat instance.
    :return: Combat instance object.
    """
    return self.__combat_instance

  def check_open_door(self, zombies: list['Zombie']) -> None:
    """
    Opens the door if all zombies are defeated.
    :param zombies: List of zombies in the level.
    """
    if self.__door and self.__door.get_state() == "closed":
      if all(not z.is_alive() for z in zombies):
        self.__door.open()

  def check_medkit_pickup(self) -> None:
    """
    Checks if hero picks up a medkit and heals.
    """
    for medkit in self.__medkits:
      if not medkit.get_used() and self.__hero.get_health() < self.__hero.get_max_health():
        hero_rect = pygame.Rect(self.__hero.get_x(), self.__hero.get_y(), 23,
                                30)
        medkit_rect = pygame.Rect(medkit.get_x(), medkit.get_y(),
                                  24,
                                  24)
        if hero_rect.colliderect(medkit_rect):
          medkit.apply(self.__hero)

  def get_pause_menu(self) -> 'PauseMenu':
    """
    Returns the pause menu, creating it if necessary.
    """
    if self.__pause_menu is None:
      self.__pause_menu = PauseMenu(self.__pause_menu_font,
                                    pygame.Rect(120, 100, 400, 220))
    return self.__pause_menu

  def handle_pause_event(self, event: EventType) -> str | None:
    """
    Handles events for the pause menu.
    :param event: Pygame event to handle.
    :return: "pause_opened", "pause_closed", or result from pause menu event
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

  def draw_pause_menu(self, surface: Surface) -> None:
    """
    Draws the pause menu if active.
    :param surface: Pygame Surface to draw the pause menu on.
    """
    pause_menu = self.get_pause_menu()
    if pause_menu.get_active():
      pause_menu.draw(surface)


class FeedbackBox:
  """Singleton class to show feedback messages on the screen with auto-hide."""

  __instance = None

  def __init__(self, font: str = FONTS.get("roboto"), width: int = 160, height: int = 24,
      margin: int = 12) -> None:
    """
    Initializes the FeedbackBox singleton.
    :param font: font name for the message text.
    :param width: Width of the feedback box.
    :param height: Height of the feedback box.
    :param margin: Margin from the screen edges.
    """
    if FeedbackBox.__instance is not None:
      raise Exception(
          "Use FeedbackBox.get_instance() to get the singleton instance.")
    self.__message = ""
    self.__font = pygame.font.Font(font, 12)
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
    :param msg: Message text to display.
    :param duration: Duration in seconds to display the message.
    :param delay: Delay in seconds before showing the message.
    """
    box = FeedbackBox.get_instance()
    box._set_message(msg, duration, delay)

  def _set_message(self, msg: str, duration: float = 5.0,
      delay: float = 0.0) -> None:
    """
    Sets the feedback message, resetting timers if the message changes.
    :param msg: Message text to display.
    :param duration: Duration in seconds to display the message.
    :param delay: Delay in seconds before showing the message.
    """
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
    :return: Current message text.
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
    :param text: Text to wrap.
    :return: List of text lines.
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

  def draw(self, surface: Surface) -> None:
    """
    Draws the feedback box on the given surface if time not expired and delay passed.
    :param surface: Pygame Surface to draw the feedback box on.
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
    """
    Initializes the pause menu.
    :param font: font for rendering text.
    :param rect: rectangle defining menu position and size.
    """
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
    """
    Returns whether the menu is in confirmation state.
    :return: True if confirming, False otherwise.
    """
    return self.__confirming

  def get_active(self) -> bool:
    """
    Returns whether the pause menu is active.
    :return: True if active, False otherwise.
    """
    return self.__active

  def open(self) -> None:
    """
    Opens the pause menu, resetting selections.
    """
    self.__active = True
    self.__selected = 0
    self.__confirming = False

  def close(self):
    """
    Closes the pause menu.
    """
    self.__active = False
    self.__confirming = False

  def draw(self, surface: Surface) -> None:
    """
    Draws the pause menu on the given surface.
    :param surface: Pygame Surface to draw the pause menu on.
    """
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

  def handle_event(self, event: EventType) -> str | None:
    """
    Handles events for the pause menu.
    :param event: the Pygame event to handle.
    """
    if not self.__active or event.type != pygame.KEYDOWN:
      return None

    if not self.__confirming:
      return self._handle_main_menu_event(event)
    else:
      return self._handle_confirm_event(event)

  def _handle_main_menu_event(self, event: EventType) -> str | None:
    """
    Handles main menu navigation events.
    :param event: the Pygame event to handle.
    :return: "continue", "main_menu", or None.
    """
    if event.key == pygame.K_UP:
      self.__selected = (self.__selected - 1) % 2
    elif event.key == pygame.K_DOWN:
      self.__selected = (self.__selected + 1) % 2
    elif event.key == pygame.K_RETURN:
      if self.__selected == 0:
        self.close()
        return "continue"
      elif self.__selected == 1:
        self.__confirming = True
        self.__confirm_selected = 1
    return None

  def _handle_confirm_event(self, event: EventType) -> str | None:
    """
    Handles confirmation dialog events.
    :param event: the Pygame event to handle.
    """
    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
      self.__confirm_selected = 1 if self.__confirm_selected == 0 else 0
      print("confirm selected set to", self.__confirm_selected)
    elif event.key == pygame.K_RETURN:
      print("confirm selected is", self.__confirm_selected)
      if self.__confirm_selected == 0:
        self.close()
        return "main_menu"
      else:
        self.__confirming = False
    return None


class TutorialLevel(Level):
  """Base class for tutorial levels."""

  def __init__(self, config: dict, hero: 'hero') -> None:
    """
    Initializes the tutorial level with fixed elements.
    :param config: Configuration dictionary for the tutorial.
    :param hero: The hero character.
    """
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
    """
    Displays the tutorial message if configured.
    """
    msg = self.__tutorial_config.get("message")
    if msg:
      FeedbackBox.get_instance().set_message(msg, 8, 1.5)

  def _generate_random_maze(self, window_size: tuple[int, int],
      wall_thickness: int = Var.DEFAULT_WALL_THICKNESS,
      cell_size: int = Var.DEFAULT_CELL_SIZE) -> list[Rect]:
    """
    Overrides maze generation to create an empty level.
    :return: Empty list of walls.
    """
    return []

  def _spawn_door(self) -> 'Door':
    """
    Spawns the door in a fixed position.
    :return: door object.
    """
    sprite_w, sprite_h = 40, 60
    x = Var.DEFAULT_WINDOW_SIZE[0] - sprite_w - 30
    y = Var.DEFAULT_WINDOW_SIZE[1] // 2 - sprite_h // 2
    return Door(x, y, DOOR_1_SPRITES)

  def _spawn_medkits(self) -> list['Medkit']:
    """
    Spawns no medkits in tutorial levels.
    :return: Empty list of medkits.
    """
    return []

  def generate_zombies(self, num_zombies: int) -> list['Zombie']:
    """
    Spawns no zombies in tutorial levels.
    :param num_zombies: Number of zombies to spawn (ignored).
    :return: Empty list of zombies.
    """
    return []


class TutorialMoveLevel(TutorialLevel):
  """Movement tutorial."""

  def __init__(self, config: dict, hero: 'hero') -> None:
    """
    Initializes the movement tutorial level.
    :param config: Configuration dictionary for the tutorial.
    :param hero: The hero character.
    """
    super().__init__(config, hero)
    self._show_message()


class TutorialCombatLevel(TutorialLevel):
  """Combat tutorial"""

  def __init__(self, config: dict, hero: 'Hero') -> None:
    """
    Initializes the movement tutorial level.
    :param config: Configuration dictionary for the tutorial.
    :param hero: The hero character.
    """
    super().__init__(config, hero)
    self._show_message()

  def generate_zombies(self, num_zombies: int) -> list['Zombie']:
    """
    One zombie in fixed position for combat tutorial.
    :param num_zombies: Number of zombies to spawn (ignored).
    :return: List with one zombie object.
    """
    from lib.core import Zombie
    sprite_w, sprite_h = (23, 30)
    x = Var.DEFAULT_WINDOW_SIZE[0] // 2 - sprite_w // 2
    y = Var.DEFAULT_WINDOW_SIZE[1] // 2 - sprite_h // 2
    return [Zombie(x, y, health=10)]


class TutorialHealLevel(TutorialLevel):
  """Healing tutorial."""

  def __init__(self, config: dict, hero: 'Hero') -> None:
    """
    Initializes the movement tutorial level.
    :param config: Configuration dictionary for the tutorial.
    :param hero: The hero character.
    """
    super().__init__(config, hero)
    self._show_message()
    self.get_hero().receive_damage(25)

  def _spawn_medkits(self) -> list['Medkit']:
    """
    One medkit in fixed position for healing tutorial.
    :return: List with one medkit object.
    """
    sprite_w, sprite_h = 24, 24
    x = Var.DEFAULT_WINDOW_SIZE[0] // 2 - sprite_w // 2
    y = Var.DEFAULT_WINDOW_SIZE[1] // 2 - sprite_h // 2
    return [Medkit(x, y, MEDKIT_SPRITES)]
