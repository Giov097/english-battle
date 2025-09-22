"""Module for generating and managing maze levels in a game."""
from pygame import Rect, Surface
import random
from enum import Enum
from abc import ABC, abstractmethod

import pygame
from pygame.event import EventType
from pygame.font import FontType
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.mixer import Channel

from Sprite.Backgrounds import BACKGROUNDS
from Sprite.Levels import DOOR_1_SPRITES, MEDKIT_SPRITES
from Sound import SOUNDS
from lib.Objects import Door, Medkit
from lib.Var import (
  DEFAULT_WINDOW_SIZE,
  DEFAULT_WALL_THICKNESS,
  DEFAULT_CELL_SIZE,
  QUESTIONS,
)
from lib.Color import Color


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
      window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE) -> None:
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
    self.__questions_set = QUESTIONS.get(self.__difficulty, {}).get(
        self.__level_type.value,
        [])
    self.__door = self._spawn_door()
    self.__medkits = self._spawn_medkits()
    self.__combat_instance: 'Combat | None' = None
    self.__combat_modal: 'BaseCombatModal | None' = None

  def get_level_type(self) -> LevelType:
    """Returns the level type."""
    return self.__level_type

  def get_difficulty(self) -> int:
    """Returns the difficulty level."""
    return self.__difficulty

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

  def _spawn_medkits(self) -> list[Medkit]:
    """Spawns medkits randomly, less likely as difficulty increases."""
    medkits = []
    sprite_w, sprite_h = 24, 24
    # Probabilidad inversa a la dificultad (más difícil, menos medkits)
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
  def _init_maze_structures(cols: int, rows: int) -> tuple[
    list[list[bool]], list[list[bool]], list[list[bool]]]:
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
      wall_thickness: int = DEFAULT_WALL_THICKNESS,
      cell_size: int = DEFAULT_CELL_SIZE) -> list[Rect]:
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
      pygame.draw.rect(surface, Color.DEFAULT_WALL_COLOR, wall)
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
      self.__combat_modal.handle_event(event)
      if self.__combat_modal.get_confirmed():
        player_answer = self.__combat_modal.get_player_answer()
        if player_answer:
          result = self.__combat_instance.process_turn(player_answer.strip())
          self.__combat_modal.set_result_text(result)
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

  def check_medkit_pickup(self, hero: 'Hero') -> None:
    """Checks if hero picks up a medkit and heals."""
    for medkit in self.__medkits:
      if not medkit.get_used() and hero.get_health() < hero.get_max_health():
        hero_rect = pygame.Rect(hero.get_x(), hero.get_y(), 23, 30)
        medkit_rect = pygame.Rect(medkit.get_x(), medkit.get_y(),
                                  24,
                                  24)
        if hero_rect.colliderect(medkit_rect):
          medkit.apply(hero)


class Combat:
  """Class to manage combat encounters with grammar questions."""

  def __init__(self, hero: 'Hero', enemy: 'Character', current_type: str,
      questions_set: list[dict[str, list[str]]]) -> None:
    """
    Initializes the Combat instance.
    """
    self.__hero: 'Hero' = hero
    self.__enemy: 'Character' = enemy
    self.__combat_type: str = current_type
    self.__active: bool = True
    self.__current_question: str | tuple[str, list[str], str] | None = None
    self.__current_answer: str | None = None
    self.__last_question: str | None = None
    self.__questions_set = questions_set if questions_set is not None else []

  def generate_question(self) -> str | tuple[str, list[str], str] | None:
    """Generates a new grammar question (word ordering or multiple choice)."""
    questions = self.__questions_set
    if not questions:
      self.__current_question = None
      self.__current_answer = None
      return ""
    if self.__combat_type == "word_ordering":
      same_question = True
      while same_question:
        words, answer = random.choice(questions)
        shuffled_words = list(words)
        random.shuffle(shuffled_words)
        question = " / ".join(shuffled_words)
        if question != self.__last_question:
          same_question = False
      self.__current_question = question
      self.__current_answer = answer
      self.__last_question = question
      return self.__current_question
    elif self.__combat_type == "multiple_choice":
      same_question = True
      while same_question:
        question, options, answer = random.choice(questions)
        if question != self.__last_question:
          same_question = False
      self.__current_question = (question, options, answer)
      self.__current_answer = answer
      self.__last_question = question
      return self.__current_question
    elif self.__combat_type == "fill_in_the_blank":
      same_question = True
      while same_question:
        question, answer = random.choice(questions)
        if question != self.__last_question:
          same_question = False
      self.__current_question = question
      self.__current_answer = answer
      self.__last_question = question
      return self.__current_question
    else:
      self.__current_question = None
      self.__current_answer = None
      self.__combat_type = None
      return ""

  def check_answer(self, player_answer: str) -> bool:
    """Checks if the player's answer is correct."""
    return player_answer.strip().lower() == self.__current_answer.strip().lower()

  def process_turn(self, player_answer: str) -> str:
    """
    Processes the turn based on player's answer. If both survive, generates a new question.
    """
    if not self.__active or not self.__hero.is_alive() or not self.__enemy.is_alive():
      pass
    if self.check_answer(player_answer):
      self.__hero.attack(self.__enemy)
      result = "¡Correcto! Atacas al enemigo."
    else:
      self.__enemy.attack(self.__hero)
      result = "Incorrecto. El enemigo te ataca."
    if not self.__enemy.is_alive() or not self.__hero.is_alive():
      self.__active = False
    else:
      self.generate_question()
    return result

  def get_current_question(self) -> str | tuple[str, list[str], str] | None:
    """Returns the current question."""
    return self.__current_question

  def get_active(self) -> bool:
    """Returns whether the combat is still active."""
    return self.__active

  def get_combat_type(self) -> str:
    """Returns the combat type."""
    return self.__combat_type


class BaseCombatModal(ABC):
  """Abstract base class for combat modals."""

  def __init__(self, font: FontType, rect: Rect, result_text: str = "") -> None:
    """
    Initializes the modal with font and rectangle.
    """
    self.__font: FontType = font
    self.__rect: Rect = rect
    self.__confirmed: bool = False
    self.__result_text: str = result_text
    self.__confirm_btn_rect: Rect | None = None
    self.__reset_btn_rect: Rect | None = None
    self.__init_buttons()

  def __init_buttons(self) -> None:
    """
    Initializes the Confirm and Reset button rectangles.
    """
    btn_w, btn_h = 100, 36
    margin = 10
    y_btn = self.__rect.y + self.__rect.height - btn_h - margin
    self.__confirm_btn_rect = pygame.Rect(
        self.__rect.x + self.__rect.width - btn_w - margin, y_btn, btn_w, btn_h)
    self.__reset_btn_rect = pygame.Rect(
        self.__rect.x + margin, y_btn, btn_w, btn_h)

  def get_confirmed(self) -> bool:
    """
    Returns whether the modal is active
    """
    return self.__confirmed

  def set_confirmed(self, value: bool) -> None:
    """
    Sets the confirmed state of the modal.
    """
    self.__confirmed = value

  def get_result_text(self) -> str:
    """
    Returns the result text to display
    """
    return self.__result_text

  def set_result_text(self, text: str) -> None:
    """
    Sets the result text to display
    """
    self.__result_text = text

  def get_rect(self) -> Rect:
    """
    Returns the rectangle of the modal.
    """
    return self.__rect

  def get_font(self) -> FontType:
    """
    Returns the font of the modal.
    """
    return self.__font

  def get_confirm_button(self) -> Rect:
    """
    Returns the confirm button rectangle.
    """
    return self.__confirm_btn_rect

  def get_reset_button(self) -> Rect:
    """
    Returns the reset button rectangle.
    """
    return self.__reset_btn_rect

  @abstractmethod
  def draw(self, surface: Surface) -> None:
    """
    Draws the modal on the given surface.
    """
    pass

  @abstractmethod
  def handle_event(self, event: EventType) -> None:
    """
    Handles events for the modal (mouse, keyboard, etc).
    """
    pass

  @abstractmethod
  def get_player_answer(self) -> str:
    """
    Returns the player's constructed answer as a string.
    """
    pass

  @abstractmethod
  def reset(self) -> None:
    """
    Resets the modal to its initial state.
    """
    pass

  def _draw_buttons(self, surface: Surface) -> None:
    """
    Draws the Confirm and Reset buttons.
    """
    pygame.draw.rect(surface, Color.WORD_BG, self.__confirm_btn_rect)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.__confirm_btn_rect, 2)
    txt2 = self.__font.render("Confirmar", True, Color.TITLE_TEXT)
    txt2_rect = txt2.get_rect(center=self.__confirm_btn_rect.center)
    surface.blit(txt2, txt2_rect)

    pygame.draw.rect(surface, Color.WORD_BG, self.__reset_btn_rect)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.__reset_btn_rect, 2)
    txt = self.__font.render("Reiniciar", True, Color.TITLE_TEXT)
    txt_rect = txt.get_rect(center=self.__reset_btn_rect.center)
    surface.blit(txt, txt_rect)


class WordOrderingModal(BaseCombatModal):
  """Modal for word ordering questions with drag-and-drop."""

  def __init__(self, question_words, font: FontType, rect: Rect,
      result_text: str = "") -> None:
    """
    Initializes the word ordering modal.
    """
    super().__init__(font, rect, result_text)
    self.__original_words = list(question_words)
    self.__shuffled_words = list(self.__original_words)
    random.shuffle(self.__shuffled_words)
    self.__answer_words = []
    self.__dragging = None
    self.__word_rects = {"shuffled": [], "answer": []}
    self.__update_word_rects()

  def __update_word_rects(self) -> None:
    """
    Updates the rectangles for the words in both areas.
    """
    margin = 10
    word_w, word_h = 90, 32
    title_height = 35
    self.__word_rects["shuffled"] = []
    for i, word in enumerate(self.__shuffled_words):
      x = self.get_rect().x + margin + i * (word_w + margin)
      y = self.get_rect().y + margin + title_height
      self.__word_rects["shuffled"].append(pygame.Rect(x, y, word_w, word_h))
    self.__word_rects["answer"] = []
    for i, word in enumerate(self.__answer_words):
      x = self.get_rect().x + margin + i * (word_w + margin)
      y = self.get_rect().y + self.get_rect().height // 2
      self.__word_rects["answer"].append(pygame.Rect(x, y, word_w, word_h))

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with words and buttons.
    """
    pygame.draw.rect(surface, Color.MODAL_BG, self.get_rect())
    title = self.get_font().render("Ordena las palabras:", True,
                                   Color.TITLE_TEXT)
    surface.blit(title, (self.get_rect().x + 10, self.get_rect().y + 5))
    for i, word in enumerate(self.__shuffled_words):
      rect: Rect = self.__word_rects["shuffled"][i]
      if word in self.__answer_words:
        pygame.draw.rect(surface, Color.WORD_BG_DISABLED, rect)
        pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
        txt = self.get_font().render(word, True, Color.WORD_TEXT_DISABLED)
      else:
        pygame.draw.rect(surface, Color.WORD_BG, rect)
        pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
        txt = self.get_font().render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (rect.x + 6, rect.y + 4))
    answer_area_rect = pygame.Rect(
        self.get_rect().x + 5,
        self.get_rect().y + self.get_rect().height // 2 - 8,
        self.get_rect().width - 10,
        48
    )
    pygame.draw.rect(surface, Color.ANSWER_AREA_BG, answer_area_rect)
    pygame.draw.rect(surface, Color.ANSWER_AREA_BORDER, answer_area_rect, 2)
    if not self.__answer_words:
      hint_txt = self.get_font().render("Arrastra aquí para formar la oración",
                                        True,
                                        Color.ANSWER_AREA_BORDER)
      hint_rect = hint_txt.get_rect(
          center=(answer_area_rect.centerx, answer_area_rect.y + 24))
      surface.blit(hint_txt, hint_rect)
    for i, word in enumerate(self.__answer_words):
      rect: Rect = self.__word_rects["answer"][i]
      pygame.draw.rect(surface, Color.ANSWER_WORD_BG, rect)
      pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
      txt = self.get_font().render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (rect.x + 6, rect.y + 4))
    if self.__dragging:
      word, _, _ = self.__dragging
      mx, my = pygame.mouse.get_pos()
      drag_rect = pygame.Rect(mx - 45, my - 16, 90, 32)
      pygame.draw.rect(surface, Color.DRAG_WORD_BG, drag_rect)
      txt = self.get_font().render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (drag_rect.x + 6, drag_rect.y + 4))
    self._draw_buttons(surface)
    if self.get_result_text():
      result_color = Color.CORRECT_ANSWER_BG if "Correcto" in self.get_result_text() else Color.WRONG_ANSWER_BG
      result_surface = self.get_font().render(self.get_result_text(), True,
                                              result_color)
      result_x = self.get_rect().x + 10
      result_y = self.get_confirm_button().bottom + 10
      surface.blit(result_surface, (result_x, result_y))

  def handle_event(self, event: EventType) -> None:
    """
    Handles mouse events for drag-and-drop and button clicks.
    """
    if event.type == MOUSEBUTTONDOWN:
      mx, my = event.pos
      if self.get_confirm_button().collidepoint(mx, my):
        self.set_confirmed(True)
        return
      if self.get_reset_button().collidepoint(mx, my):
        self.__answer_words = []
        self.set_confirmed(False)
        self.__update_word_rects()
        return
      for i, rect in enumerate(self.__word_rects["shuffled"]):
        word = self.__shuffled_words[i]
        if rect.collidepoint(mx, my) and word not in self.__answer_words:
          self.__dragging = (word, "shuffled", i)
          return
      for i, rect in enumerate(self.__word_rects["answer"]):
        word = self.__answer_words[i]
        if rect.collidepoint(mx, my):
          self.__dragging = (word, "answer", i)
          return
    elif event.type == MOUSEBUTTONUP and self.__dragging:
      mx, my = event.pos
      word, from_area, _ = self.__dragging
      answer_area = pygame.Rect(self.get_rect().x,
                                self.get_rect().y + self.get_rect().height // 2,
                                self.get_rect().width,
                                self.get_rect().height // 2)
      shuffled_area = pygame.Rect(self.get_rect().x, self.get_rect().y,
                                  self.get_rect().width,
                                  self.get_rect().height // 2)
      if from_area == "shuffled" and answer_area.collidepoint(mx, my):
        if word not in self.__answer_words:
          self.__answer_words.append(word)
      elif from_area == "answer" and shuffled_area.collidepoint(mx, my):
        if word in self.__answer_words:
          self.__answer_words.remove(word)
      self.__dragging = None
      self.__update_word_rects()
    elif event.type == MOUSEMOTION and self.__dragging:
      pass

  def get_player_answer(self) -> str:
    """
    Returns the player's constructed answer as a string.
    """
    return " ".join(self.__answer_words)

  def reset(self) -> None:
    """
    Resets the modal to initial state.
    """
    self.__answer_words = []
    self.set_confirmed(False)
    self.__update_word_rects()


class MultipleChoiceModal(BaseCombatModal):
  """Modal for multiple choice questions."""

  def __init__(self, question: str, options: list[str], font: FontType,
      rect: Rect, result_text: str = "") -> None:
    """
    Initializes the multiple choice modal.
    """
    super().__init__(font, rect, result_text)
    self.__question = question
    self.__options = options
    self.__selected_index = None
    self.__option_rects = []
    self.__update_option_rects()

  def __update_option_rects(self) -> None:
    """
    Updates the rectangles for the options.
    """
    margin = 10
    option_h = 36
    option_w = self.get_rect().width - 2 * margin
    start_y = self.get_rect().y + 50
    self.__option_rects = []
    for i, _ in enumerate(self.__options):
      y = start_y + i * (option_h + margin)
      self.__option_rects.append(
          pygame.Rect(self.get_rect().x + margin, y, option_w, option_h))

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with question, options, and buttons.
    """
    pygame.draw.rect(surface, Color.MODAL_BG, self.get_rect())
    title = self.get_font().render("Elige la respuesta correcta:", True,
                                   Color.TITLE_TEXT)
    surface.blit(title, (self.get_rect().x + 10, self.get_rect().y + 5))
    question_txt = self.get_font().render(self.__question, True,
                                          Color.TITLE_TEXT)
    surface.blit(question_txt, (self.get_rect().x + 10, self.get_rect().y + 30))
    for i, option in enumerate(self.__options):
      rect: Rect = self.__option_rects[i]
      bg_color = Color.ANSWER_WORD_BG if self.__selected_index == i else Color.WORD_BG
      border_color = Color.ANSWER_AREA_BORDER if self.__selected_index == i else Color.WORD_BORDER
      pygame.draw.rect(surface, bg_color, rect)
      pygame.draw.rect(surface, border_color, rect, 2)
      txt = self.get_font().render(option, True, Color.TITLE_TEXT)
      surface.blit(txt, (rect.x + 8, rect.y + 6))
      if self.__selected_index == i:
        pygame.draw.circle(surface, Color.ANSWER_AREA_BORDER,
                           (rect.right - 18, rect.centery), 10, 0)
    self._draw_buttons(surface)
    if self.get_result_text():
      result_color = Color.CORRECT_ANSWER_BG if "Correcto" in self.get_result_text() else Color.WRONG_ANSWER_BG
      result_surface = self.get_font().render(self.get_result_text(), True,
                                              result_color)
      result_x = self.get_rect().x + 10
      result_y = self.get_confirm_button().bottom + 10
      surface.blit(result_surface, (result_x, result_y))

  def handle_event(self, event: EventType) -> None:
    """
    Handles mouse events for option selection and button clicks.
    """
    if event.type == MOUSEBUTTONDOWN:
      mx, my = event.pos
      if self.get_confirm_button().collidepoint(mx, my):
        self.set_confirmed(True)
        return
      if self.get_reset_button().collidepoint(mx, my):
        self.__selected_index = None
        self.set_confirmed(False)
        return
      for i, rect in enumerate(self.__option_rects):
        if rect.collidepoint(mx, my):
          self.__selected_index = i
          return

  def get_player_answer(self) -> str:
    """
    Returns the selected option as the player's answer.
    """
    if self.__selected_index is not None:
      return self.__options[self.__selected_index]
    return ""

  def reset(self) -> None:
    """
    Resets the modal to initial state.
    """
    self.__selected_index = None
    self.set_confirmed(False)


class FillGapsModal(BaseCombatModal):
  """Modal for fill-in-the-blank questions with free text input."""

  def __init__(self, question: str, font: FontType, rect: Rect,
      result_text: str = "") -> None:
    """
    Initializes the fill-in-the-blank modal.
    """
    super().__init__(font, rect, result_text)
    self.__question = question
    self.__input_text = ""
    self.__active_input = True
    self.__input_rect = pygame.Rect(
        self.get_rect().x + 20,
        self.get_rect().y + self.get_rect().height // 2 - 18,
        self.get_rect().width - 40,
        36
    )
    self.__cursor_visible = True
    self.__cursor_counter = 0

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with a prompt, input box, and buttons.
    """
    # Fondo semitransparente para modal
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    # Área principal del modal
    pygame.draw.rect(surface, Color.MODAL_BG, self.get_rect(), border_radius=12)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.get_rect(), 2,
                     border_radius=12)

    # Prompt
    title = self.get_font().render("Completa el espacio en blanco:", True,
                                   Color.TITLE_TEXT)
    surface.blit(title, (self.get_rect().x + 20, self.get_rect().y + 18))

    # Pregunta
    question_txt = self.get_font().render(self.__question, True,
                                          Color.TITLE_TEXT)
    surface.blit(question_txt, (self.get_rect().x + 20, self.get_rect().y + 60))

    # Input box
    pygame.draw.rect(surface, Color.ANSWER_AREA_BG, self.__input_rect,
                     border_radius=8)
    pygame.draw.rect(surface, Color.ANSWER_AREA_BORDER, self.__input_rect, 2,
                     border_radius=8)
    input_display = self.__input_text
    if self.__active_input and self.__cursor_visible:
      input_display += "|"
    input_txt = self.get_font().render(input_display, True, Color.TITLE_TEXT)
    surface.blit(input_txt, (self.__input_rect.x + 8, self.__input_rect.y + 6))

    # Botones
    self._draw_buttons(surface)

    # Resultado
    if self.get_result_text():
      result_color = Color.CORRECT_ANSWER_BG if "Correcto" in self.get_result_text() else Color.WRONG_ANSWER_BG
      result_surface = self.get_font().render(self.get_result_text(), True,
                                              result_color)
      result_x = self.get_rect().x + 20
      result_y = self.get_confirm_button().bottom + 14
      surface.blit(result_surface, (result_x, result_y))

    # Cursor blink
    self.__cursor_counter += 1
    if self.__cursor_counter > 30:
      self.__cursor_visible = not self.__cursor_visible
      self.__cursor_counter = 0

  def handle_event(self, event: EventType) -> None:
    """
    Handles keyboard and mouse events for text input and buttons.
    """
    if event.type == MOUSEBUTTONDOWN:
      mx, my = event.pos
      if self.__input_rect.collidepoint(mx, my):
        self.__active_input = True
      else:
        self.__active_input = False
      if self.get_confirm_button().collidepoint(mx, my):
        self.set_confirmed(True)
        return
      if self.get_reset_button().collidepoint(mx, my):
        self.__input_text = ""
        self.set_result_text("")
        self.set_confirmed(False)
    elif event.type == pygame.KEYDOWN and self.__active_input:
      if event.key == pygame.K_BACKSPACE:
        self.__input_text = self.__input_text[:-1]
      elif event.key == pygame.K_RETURN:
        self.set_confirmed(True)
      elif event.key == pygame.K_TAB:
        pass
      else:
        char = event.unicode
        if len(char) == 1 and len(self.__input_text) < 40:
          self.__input_text += char

  def get_player_answer(self) -> str:
    """
    Returns the user's input as the answer.
    """
    return self.__input_text.strip()

  def reset(self) -> None:
    """
    Resets the modal to initial state.
    """
    self.__active_input = True
    self.__cursor_visible = True
    self.__input_text = ""
    self.set_confirmed(False)
    self.set_result_text("")
