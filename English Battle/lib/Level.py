"""Module for generating and managing maze levels in a game."""
from pygame import Rect, Surface
import random
from enum import Enum
from abc import ABC, abstractmethod

import pygame
from pygame.font import FontType
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.mixer import Channel

from Sprite.Backgrounds import BACKGROUNDS
from Sprite.Levels import DOOR_1_SPRITES
from Sound import SOUNDS
from lib.Var import (
  DEFAULT_WINDOW_SIZE,
  DEFAULT_WALL_THICKNESS,
  DEFAULT_CELL_SIZE,
  DEFAULT_DEATH_FADE_DURATION,
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
    self._death_handled: None = None
    self.window_size: tuple[int, int] = window_size
    self.background_name: str = background_name
    self.background: Surface = pygame.transform.scale(
        BACKGROUNDS[self.background_name], self.window_size
    )
    self.maze_walls: list[Rect] = self._generate_random_maze(self.window_size)
    self._death_fade_active: bool = False
    self._death_fade_start_time: int | None = None
    self._death_fade_duration: float = DEFAULT_DEATH_FADE_DURATION
    self.difficulty: int = difficulty
    self.level_type: LevelType = level_type
    self.questions_set = QUESTIONS.get(self.difficulty, {}).get(
        self.level_type.value,
        [])
    self.combat_instance = None
    self.combat_modal = None
    self.door = self._spawn_door()

  def _spawn_door(self) -> 'Door':
    """Spawns a door in a valid position (not colliding with maze walls)."""
    sprite_w, sprite_h = 40, 60
    max_attempts = 100
    for _ in range(max_attempts):
      x = random.randint(0, self.window_size[0] - sprite_w)
      y = random.randint(0, self.window_size[1] - sprite_h)
      rect = pygame.Rect(x, y, sprite_w, sprite_h)
      if not self.check_collision(rect):
        return Door((x, y), DOOR_1_SPRITES)
    # Si no encuentra lugar, la pone en (0,0)
    return Door((0, 0), DOOR_1_SPRITES)

  def get_door(self) -> 'Door':
    """Returns the door object."""
    return self.door

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
    surface.blit(self.background, (0, 0))

  def draw_maze(self, surface: Surface) -> None:
    """Draws the maze walls and the door on the given surface."""
    for wall in self.maze_walls:
      pygame.draw.rect(surface, (80, 80, 80), wall)
    # Dibuja la puerta
    if self.door:
      if self.door.state == "opening":
        self.door.animate_opening()
      self.door.draw(surface)

  def check_collision(self, rect: Rect) -> bool:
    """Returns True if rect collides with any maze wall."""
    for wall in self.maze_walls:
      if rect.colliderect(wall):
        return True
    return False

  def handle_player_death(self, window_surface: Surface) -> None:
    """
    Handles the death fade effect and sound sequence when the player dies.
    """
    if not self._death_fade_active:
      self._death_fade_active = True
      self._death_fade_start_time = pygame.time.get_ticks()
      self._play_death_sounds()
    elapsed = (pygame.time.get_ticks() - self._death_fade_start_time) / 1000.0
    alpha = min(255, int((elapsed / self._death_fade_duration) * 255))
    self._draw_death_fade(window_surface, alpha)
    self.update_death_sounds()
    if elapsed >= self._death_fade_duration:
      pygame.quit()

  def _draw_death_fade(self, surface: Surface, alpha: int) -> None:
    """
    Draws a black overlay with the given alpha for the death fade effect.
    """
    overlay = pygame.Surface(self.window_size)
    overlay.fill((0, 0, 0))
    overlay.set_alpha(alpha)
    surface.blit(overlay, (0, 0))

  def _play_death_sounds(self) -> None:
    """
    Plays beep sound twice and then flatline, each after the previous finishes.
    """
    channel: Channel = pygame.mixer.find_channel()
    if channel is None:
      return

    sounds = [SOUNDS["beep"], SOUNDS["beep"], SOUNDS["flatline"]]
    self._death_sound_index: int = 0

    def play_next_sound() -> None:
      """Plays the next sound"""
      if self._death_sound_index < len(sounds):
        channel.play(sounds[self._death_sound_index])
        self._death_sound_index += 1

    def check_channel_end() -> None:
      """Checks if the channel is not busy"""
      if not channel.get_busy() and self._death_sound_index < len(sounds):
        play_next_sound()

    play_next_sound()

    self._check_death_sound_end = check_channel_end

  def update_death_sounds(self) -> None:
    """
    Call in the main loop to update the death sound sequence.
    """
    if hasattr(self, "_check_death_sound_end"):
      self._check_death_sound_end()

  def generate_zombies(self, num_zombies: int) -> list['Zombie']:
    """Generates zombies at random positions not colliding with walls."""
    from lib.Core import Zombie
    zombies: list[Zombie] = []
    sprite_w, sprite_h = (23, 30)
    for _ in range(num_zombies):
      valid_spawn = False
      while not valid_spawn:
        x = random.randint(0, self.window_size[0] - sprite_w)
        y = random.randint(0, self.window_size[1] - sprite_h)
        rect = pygame.Rect(x, y, sprite_w, sprite_h)
        if not self.check_collision(rect):
          valid_spawn = True
      health = 10 + (self.difficulty - 1) * 5
      zombies.append(Zombie(x, y, health=health))
    return zombies

  def start_combat(self, character: 'Character', zombies: list['Zombie'],
      font: FontType) -> bool:
    """Starts combat if the hero is near a zombie."""
    if self.combat_instance is None or not self.combat_instance.active:
      for zombie in zombies:
        if zombie.is_alive() and character.can_attack(zombie):
          self.combat_instance = Combat(character, zombie,
                                        self.level_type.value,
                                        self.questions_set)
          question = self.combat_instance.generate_question()
          if self.level_type == LevelType.WORD_ORDERING:
            words = question.split(" / ")
            self.combat_modal = WordOrderingModal(words, font,
                                                  pygame.Rect(40, 100, 560,
                                                              260))
          elif self.level_type == LevelType.MULTIPLE_CHOICE:
            q, options, _ = self.combat_instance.current_question
            self.combat_modal = MultipleChoiceModal(q, options, font,
                                                    pygame.Rect(40, 100, 560,
                                                                260))
          elif self.level_type == LevelType.FILL_IN_THE_BLANK:
            self.combat_modal = FillGapsModal(question, font,
                                              pygame.Rect(40, 100, 560, 260))
          else:
            self.combat_modal = None
          return True
    return False

  def handle_combat_event(self, event, font) -> None:
    """Handles events for combat and the modal."""
    if self.combat_instance is not None and self.combat_instance.active and self.combat_modal:
      self.combat_modal.handle_event(event)
      if self.combat_modal.confirmed:
        player_answer = self.combat_modal.get_player_answer()
        if player_answer:
          result = self.combat_instance.process_turn(player_answer.strip())
          self.combat_modal.result_text = result
          if self.combat_instance.active:
            if self.combat_instance.current_type == "word_ordering":
              words = self.combat_instance.current_question.split(" / ")
              self.combat_modal = WordOrderingModal(words, font,
                                                    pygame.Rect(40, 100, 560,
                                                                260),
                                                    result_text=result)
            elif self.combat_instance.current_type == "multiple_choice":
              q, options, _ = self.combat_instance.current_question
              self.combat_modal = MultipleChoiceModal(q, options, font,
                                                      pygame.Rect(40, 100, 560,
                                                                  260),
                                                      result_text=result)
            elif self.combat_instance.current_type == "fill_in_the_blank":
              self.combat_modal = FillGapsModal(
                  self.combat_instance.current_question, font,
                  pygame.Rect(40, 100, 560, 260), result_text=result)
            else:
              self.combat_modal = None
          else:
            self.combat_modal = None
        else:
          self.combat_modal.confirmed = False

  def get_combat_modal(self) -> 'BaseCombatModal':
    """Returns the current modal if it exists."""
    return self.combat_modal

  def get_combat_instance(self) -> 'Combat':
    """Returns the current combat instance."""
    return self.combat_instance

  def check_open_door(self, zombies: list['Zombie']) -> None:
    """Opens the door if all zombies are defeated."""
    if self.door and self.door.state == "closed":
      if all(not z.is_alive() for z in zombies):
        self.door.open()


class Combat:
  """Class to manage combat encounters with grammar questions."""

  def __init__(self, hero: 'Hero', enemy: 'Character', current_type: str,
      questions_set: list[dict[str, list[str]]]) -> None:
    """
    Initializes the Combat instance.
    """
    self.hero: 'Hero' = hero
    self.enemy: 'Character' = enemy
    self.current_type: str = current_type
    self.active: bool = True
    self.current_question: str | None = None
    self.current_answer: str | None = None
    self._last_question: str | None = None
    self.questions_set = questions_set if questions_set is not None else []

  def generate_question(self) -> str | tuple[str, list[str], str] | None:
    """Generates a new grammar question (word ordering or multiple choice)."""
    questions = self.questions_set
    if not questions:
      self.current_question = None
      self.current_answer = None
      return ""
    if self.current_type == "word_ordering":
      same_question = True
      while same_question:
        words, answer = random.choice(questions)
        shuffled_words = list(words)
        random.shuffle(shuffled_words)
        question = " / ".join(shuffled_words)
        if question != self._last_question:
          same_question = False
      self.current_question = question
      self.current_answer = answer
      self._last_question = question
      return self.current_question
    elif self.current_type == "multiple_choice":
      same_question = True
      while same_question:
        question, options, answer = random.choice(questions)
        if question != self._last_question:
          same_question = False
      self.current_question = (question, options, answer)
      self.current_answer = answer
      self._last_question = question
      return self.current_question
    elif self.current_type == "fill_in_the_blank":
      same_question = True
      while same_question:
        question, answer = random.choice(questions)
        if question != self._last_question:
          same_question = False
      self.current_question = question
      self.current_answer = answer
      self._last_question = question
      return self.current_question
    else:
      self.current_question = None
      self.current_answer = None
      self.current_type = None
      return ""

  def check_answer(self, player_answer: str) -> bool:
    """Checks if the player's answer is correct."""
    return player_answer.strip().lower() == self.current_answer.strip().lower()

  def process_turn(self, player_answer: str) -> str:
    """
    Processes the turn based on player's answer. If both survive, generates a new question.
    """
    if not self.active or not self.hero.is_alive() or not self.enemy.is_alive():
      pass
    if self.check_answer(player_answer):
      self.hero.attack(self.enemy)
      result = "¡Correcto! Atacas al enemigo."
    else:
      self.enemy.attack(self.hero)
      result = "Incorrecto. El enemigo te ataca."
    if not self.enemy.is_alive() or not self.hero.is_alive():
      self.active = False
    else:
      self.generate_question()
    return result


class BaseCombatModal(ABC):
  """Abstract base class for combat modals."""

  def __init__(self, font: FontType, rect: Rect, result_text: str = "") -> None:
    """
    Initializes the modal with font and rectangle.
    """
    self.font = font
    self.rect = rect
    self.confirmed = False
    self.result_text = result_text
    self._init_buttons()

  def _init_buttons(self) -> None:
    """
    Initializes the Confirm and Reset button rectangles.
    """
    btn_w, btn_h = 100, 36
    margin = 10
    y_btn = self.rect.y + self.rect.height - btn_h - margin
    self.confirm_btn_rect = pygame.Rect(
        self.rect.x + self.rect.width - btn_w - margin, y_btn, btn_w, btn_h)
    self.reset_btn_rect = pygame.Rect(
        self.rect.x + margin, y_btn, btn_w, btn_h)

  @abstractmethod
  def draw(self, surface: Surface) -> None:
    """
    Draws the modal on the given surface.
    """
    pass

  @abstractmethod
  def handle_event(self, event) -> None:
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
    pygame.draw.rect(surface, Color.WORD_BG, self.confirm_btn_rect)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.confirm_btn_rect, 2)
    txt2 = self.font.render("Confirmar", True, Color.TITLE_TEXT)
    txt2_rect = txt2.get_rect(center=self.confirm_btn_rect.center)
    surface.blit(txt2, txt2_rect)

    pygame.draw.rect(surface, Color.WORD_BG, self.reset_btn_rect)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.reset_btn_rect, 2)
    txt = self.font.render("Reiniciar", True, Color.TITLE_TEXT)
    txt_rect = txt.get_rect(center=self.reset_btn_rect.center)
    surface.blit(txt, txt_rect)


class WordOrderingModal(BaseCombatModal):
  """Modal for word ordering questions with drag-and-drop."""

  def __init__(self, question_words, font: FontType, rect: Rect,
      result_text: str = "") -> None:
    """
    Initializes the word ordering modal.
    """
    super().__init__(font, rect, result_text)
    self.original_words = list(question_words)
    self.shuffled_words = list(self.original_words)
    random.shuffle(self.shuffled_words)
    self.answer_words = []
    self.dragging = None
    self.word_rects = {"shuffled": [], "answer": []}
    self._update_word_rects()

  def _update_word_rects(self) -> None:
    """
    Updates the rectangles for the words in both areas.
    """
    margin = 10
    word_w, word_h = 90, 32
    title_height = 35
    self.word_rects["shuffled"] = []
    for i, word in enumerate(self.shuffled_words):
      x = self.rect.x + margin + i * (word_w + margin)
      y = self.rect.y + margin + title_height
      self.word_rects["shuffled"].append(pygame.Rect(x, y, word_w, word_h))
    self.word_rects["answer"] = []
    for i, word in enumerate(self.answer_words):
      x = self.rect.x + margin + i * (word_w + margin)
      y = self.rect.y + self.rect.height // 2
      self.word_rects["answer"].append(pygame.Rect(x, y, word_w, word_h))

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with words and buttons.
    """
    pygame.draw.rect(surface, Color.MODAL_BG, self.rect)
    title = self.font.render("Ordena las palabras:", True, Color.TITLE_TEXT)
    surface.blit(title, (self.rect.x + 10, self.rect.y + 5))
    for i, word in enumerate(self.shuffled_words):
      rect = self.word_rects["shuffled"][i]
      if word in self.answer_words:
        pygame.draw.rect(surface, Color.WORD_BG_DISABLED, rect)
        pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
        txt = self.font.render(word, True, Color.WORD_TEXT_DISABLED)
      else:
        pygame.draw.rect(surface, Color.WORD_BG, rect)
        pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
        txt = self.font.render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (rect.x + 6, rect.y + 4))
    answer_area_rect = pygame.Rect(
        self.rect.x + 5,
        self.rect.y + self.rect.height // 2 - 8,
        self.rect.width - 10,
        48
    )
    pygame.draw.rect(surface, Color.ANSWER_AREA_BG, answer_area_rect)
    pygame.draw.rect(surface, Color.ANSWER_AREA_BORDER, answer_area_rect, 2)
    if not self.answer_words:
      hint_txt = self.font.render("Arrastra aquí para formar la oración", True,
                                  Color.ANSWER_AREA_BORDER)
      hint_rect = hint_txt.get_rect(
          center=(answer_area_rect.centerx, answer_area_rect.y + 24))
      surface.blit(hint_txt, hint_rect)
    for i, word in enumerate(self.answer_words):
      rect = self.word_rects["answer"][i]
      pygame.draw.rect(surface, Color.ANSWER_WORD_BG, rect)
      pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
      txt = self.font.render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (rect.x + 6, rect.y + 4))
    if self.dragging:
      word, _, _ = self.dragging
      mx, my = pygame.mouse.get_pos()
      drag_rect = pygame.Rect(mx - 45, my - 16, 90, 32)
      pygame.draw.rect(surface, Color.DRAG_WORD_BG, drag_rect)
      txt = self.font.render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (drag_rect.x + 6, drag_rect.y + 4))
    self._draw_buttons(surface)
    if self.result_text:
      result_color = Color.CORRECT_ANSWER_BG if "Correcto" in self.result_text else Color.WRONG_ANSWER_BG
      result_surface = self.font.render(self.result_text, True, result_color)
      result_x = self.rect.x + 10
      result_y = self.confirm_btn_rect.bottom + 10
      surface.blit(result_surface, (result_x, result_y))

  def handle_event(self, event) -> None:
    """
    Handles mouse events for drag-and-drop and button clicks.
    """
    if event.type == MOUSEBUTTONDOWN:
      mx, my = event.pos
      if self.confirm_btn_rect.collidepoint(mx, my):
        self.confirmed = True
        return
      if self.reset_btn_rect.collidepoint(mx, my):
        self.answer_words = []
        self.confirmed = False
        self._update_word_rects()
        return
      for i, rect in enumerate(self.word_rects["shuffled"]):
        word = self.shuffled_words[i]
        if rect.collidepoint(mx, my) and word not in self.answer_words:
          self.dragging = (word, "shuffled", i)
          return
      for i, rect in enumerate(self.word_rects["answer"]):
        word = self.answer_words[i]
        if rect.collidepoint(mx, my):
          self.dragging = (word, "answer", i)
          return
    elif event.type == MOUSEBUTTONUP and self.dragging:
      mx, my = event.pos
      word, from_area, _ = self.dragging
      answer_area = pygame.Rect(self.rect.x,
                                self.rect.y + self.rect.height // 2,
                                self.rect.width, self.rect.height // 2)
      shuffled_area = pygame.Rect(self.rect.x, self.rect.y,
                                  self.rect.width, self.rect.height // 2)
      if from_area == "shuffled" and answer_area.collidepoint(mx, my):
        if word not in self.answer_words:
          self.answer_words.append(word)
      elif from_area == "answer" and shuffled_area.collidepoint(mx, my):
        if word in self.answer_words:
          self.answer_words.remove(word)
      self.dragging = None
      self._update_word_rects()
    elif event.type == MOUSEMOTION and self.dragging:
      pass

  def get_player_answer(self) -> str:
    """
    Returns the player's constructed answer as a string.
    """
    return " ".join(self.answer_words)

  def reset(self) -> None:
    """
    Resets the modal to initial state.
    """
    self.answer_words = []
    self.confirmed = False
    self._update_word_rects()


class MultipleChoiceModal(BaseCombatModal):
  """Modal for multiple choice questions."""

  def __init__(self, question: str, options: list[str], font: FontType,
      rect: Rect, result_text: str = "") -> None:
    """
    Initializes the multiple choice modal.
    """
    super().__init__(font, rect, result_text)
    self.question = question
    self.options = options
    self.selected_index = None
    self.option_rects = []
    self._update_option_rects()

  def _update_option_rects(self) -> None:
    """
    Updates the rectangles for the options.
    """
    margin = 10
    option_h = 36
    option_w = self.rect.width - 2 * margin
    start_y = self.rect.y + 50
    self.option_rects = []
    for i, _ in enumerate(self.options):
      y = start_y + i * (option_h + margin)
      self.option_rects.append(
          pygame.Rect(self.rect.x + margin, y, option_w, option_h))

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with question, options, and buttons.
    """
    pygame.draw.rect(surface, Color.MODAL_BG, self.rect)
    title = self.font.render("Elige la respuesta correcta:", True,
                             Color.TITLE_TEXT)
    surface.blit(title, (self.rect.x + 10, self.rect.y + 5))
    question_txt = self.font.render(self.question, True, Color.TITLE_TEXT)
    surface.blit(question_txt, (self.rect.x + 10, self.rect.y + 30))
    for i, option in enumerate(self.options):
      rect = self.option_rects[i]
      bg_color = Color.ANSWER_WORD_BG if self.selected_index == i else Color.WORD_BG
      border_color = Color.ANSWER_AREA_BORDER if self.selected_index == i else Color.WORD_BORDER
      pygame.draw.rect(surface, bg_color, rect)
      pygame.draw.rect(surface, border_color, rect, 2)
      txt = self.font.render(option, True, Color.TITLE_TEXT)
      surface.blit(txt, (rect.x + 8, rect.y + 6))
      if self.selected_index == i:
        pygame.draw.circle(surface, Color.ANSWER_AREA_BORDER,
                           (rect.right - 18, rect.centery), 10, 0)
    self._draw_buttons(surface)
    if self.result_text:
      result_color = Color.CORRECT_ANSWER_BG if "Correcto" in self.result_text else Color.WRONG_ANSWER_BG
      result_surface = self.font.render(self.result_text, True, result_color)
      result_x = self.rect.x + 10
      result_y = self.confirm_btn_rect.bottom + 10
      surface.blit(result_surface, (result_x, result_y))

  def handle_event(self, event) -> None:
    """
    Handles mouse events for option selection and button clicks.
    """
    if event.type == MOUSEBUTTONDOWN:
      mx, my = event.pos
      if self.confirm_btn_rect.collidepoint(mx, my):
        self.confirmed = True
        return
      if self.reset_btn_rect.collidepoint(mx, my):
        self.selected_index = None
        self.confirmed = False
        return
      for i, rect in enumerate(self.option_rects):
        if rect.collidepoint(mx, my):
          self.selected_index = i
          return

  def get_player_answer(self) -> str:
    """
    Returns the selected option as the player's answer.
    """
    if self.selected_index is not None:
      return self.options[self.selected_index]
    return ""

  def reset(self) -> None:
    """
    Resets the modal to initial state.
    """
    self.selected_index = None
    self.confirmed = False


class FillGapsModal(BaseCombatModal):
  """Modal for fill-in-the-blank questions with free text input."""

  def __init__(self, question: str, font: FontType, rect: Rect,
      result_text: str = "") -> None:
    """
    Initializes the fill-in-the-blank modal.
    """
    super().__init__(font, rect, result_text)
    self.question = question
    self.input_text = ""
    self.active_input = True
    self.input_rect = pygame.Rect(
        self.rect.x + 20,
        self.rect.y + self.rect.height // 2 - 18,
        self.rect.width - 40,
        36
    )
    self.cursor_visible = True
    self.cursor_counter = 0

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with a prompt, input box, and buttons.
    """
    # Fondo semitransparente para modal
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    # Área principal del modal
    pygame.draw.rect(surface, Color.MODAL_BG, self.rect, border_radius=12)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.rect, 2, border_radius=12)

    # Prompt
    title = self.font.render("Completa el espacio en blanco:", True,
                             Color.TITLE_TEXT)
    surface.blit(title, (self.rect.x + 20, self.rect.y + 18))

    # Pregunta
    question_txt = self.font.render(self.question, True, Color.TITLE_TEXT)
    surface.blit(question_txt, (self.rect.x + 20, self.rect.y + 60))

    # Input box
    pygame.draw.rect(surface, Color.ANSWER_AREA_BG, self.input_rect,
                     border_radius=8)
    pygame.draw.rect(surface, Color.ANSWER_AREA_BORDER, self.input_rect, 2,
                     border_radius=8)
    input_display = self.input_text
    if self.active_input and self.cursor_visible:
      input_display += "|"
    input_txt = self.font.render(input_display, True, Color.TITLE_TEXT)
    surface.blit(input_txt, (self.input_rect.x + 8, self.input_rect.y + 6))

    # Botones
    self._draw_buttons(surface)

    # Resultado
    if self.result_text:
      result_color = Color.CORRECT_ANSWER_BG if "Correcto" in self.result_text else Color.WRONG_ANSWER_BG
      result_surface = self.font.render(self.result_text, True, result_color)
      result_x = self.rect.x + 20
      result_y = self.confirm_btn_rect.bottom + 14
      surface.blit(result_surface, (result_x, result_y))

    # Cursor blink
    self.cursor_counter += 1
    if self.cursor_counter > 30:
      self.cursor_visible = not self.cursor_visible
      self.cursor_counter = 0

  def handle_event(self, event) -> None:
    """
    Handles keyboard and mouse events for text input and buttons.
    """
    if event.type == MOUSEBUTTONDOWN:
      mx, my = event.pos
      if self.input_rect.collidepoint(mx, my):
        self.active_input = True
      else:
        self.active_input = False
      if self.confirm_btn_rect.collidepoint(mx, my):
        self.confirmed = True
        return
      if self.reset_btn_rect.collidepoint(mx, my):
        self.input_text = ""
        self.confirmed = False
        self.result_text = ""
    elif event.type == pygame.KEYDOWN and self.active_input:
      if event.key == pygame.K_BACKSPACE:
        self.input_text = self.input_text[:-1]
      elif event.key == pygame.K_RETURN:
        self.confirmed = True
      elif event.key == pygame.K_TAB:
        pass
      else:
        char = event.unicode
        if len(char) == 1 and len(self.input_text) < 40:
          self.input_text += char

  def get_player_answer(self) -> str:
    """
    Returns the user's input as the answer.
    """
    return self.input_text.strip()

  def reset(self) -> None:
    """
    Resets the modal to initial state.
    """
    self.input_text = ""
    self.confirmed = False
    self.active_input = True
    self.cursor_visible = True
    self.result_text = ""


class Door:
  """Class representing a door in the level."""

  def __init__(self, position: tuple[int, int],
      sprite_dict: dict[str, 'Surface']) -> None:
    """
    Initializes the Door object.
    """
    self.position = position
    self.sprites = sprite_dict
    self.state = "closed"
    self.opening_frame = 0
    self.image = self.sprites["closed"]
    self.open_sounds = [SOUNDS.get("doormove9"), SOUNDS.get("doormove10")]

  def open(self) -> None:
    """
    Starts the opening animation.
    """
    if self.state == "closed":
      if self.open_sounds:
        channel = pygame.mixer.find_channel()
        if channel:
          random.choice(self.open_sounds).play()
      self.state = "opening"
      self.opening_frame = 0

  def animate_opening(self) -> None:
    """
    Animates the door opening using available sprites.
    """
    if self.state == "opening":
      frames = [
        self.sprites.get("opening-1"),
        self.sprites.get("opening-2"),
        self.sprites.get("opening-3"),
        self.sprites.get("open")
      ]
      if self.opening_frame < len(frames):
        self.image = frames[self.opening_frame]
        self.opening_frame += 1
      else:
        self.image = self.sprites["open"]
        self.state = "open"

  def draw(self, surface: 'Surface') -> None:
    """
    Draws the door on the given surface.
    """
    surface.blit(self.image, self.position)
