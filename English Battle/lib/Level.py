"""Module for generating and managing maze levels in a game."""
from pygame import Rect, Surface
import pygame
import random
from enum import Enum

from pygame.mixer import Channel

from Sprite.Backgrounds import BACKGROUNDS
from Sound import SOUNDS
from lib.Var import (
  DEFAULT_WINDOW_SIZE,
  DEFAULT_WALL_THICKNESS,
  DEFAULT_CELL_SIZE,
  DEFAULT_DEATH_FADE_DURATION,
  QUESTIONS,
)


class LevelType(Enum):
  WORD_ORDERING = "word_ordering"
  FILL_IN_THE_BLANK = "fill_in_the_blank"
  MULTIPLE_CHOICE = "multiple_choice"


class Level:
  """Class to manage the game level, including background and maze."""

  def __init__(self, window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
      background_name: str = "grass",
      difficulty: int = 1,
      level_type: LevelType = LevelType.WORD_ORDERING) -> None:
    self._death_handled: None = None
    self.window_size: tuple[int, int] = window_size
    self.background_name: str = background_name
    self.background: Surface = pygame.transform.scale(
        BACKGROUNDS[self.background_name], self.window_size
    )
    self.maze_walls: list[Rect] = self._generate_random_maze(self.window_size)
    self._death_fade_active: bool = False
    self._death_fade_start_time: int | None = None
    self._death_fade_duration: float = DEFAULT_DEATH_FADE_DURATION  # seconds
    self.difficulty: int = difficulty
    self.level_type: LevelType = level_type
    # Selecciona el set de preguntas según dificultad y tipo
    self.questions_set = QUESTIONS.get(self.difficulty, {}).get(self.level_type.value,
                                                                [])

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
    """Draws the maze walls on the given surface."""
    for wall in self.maze_walls:
      pygame.draw.rect(surface, (80, 80, 80), wall)

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
    # Calcula el progreso del fade
    elapsed = (pygame.time.get_ticks() - self._death_fade_start_time) / 1000.0
    alpha = min(255, int((elapsed / self._death_fade_duration) * 255))
    self._draw_death_fade(window_surface, alpha)
    self.update_death_sounds()
    # Si terminó el fade, puede mostrar mensaje final o terminar el juego
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


class Combat:
  """Class to manage combat encounters with grammar questions."""

  def __init__(self, hero: 'Hero', enemy: 'Character',
      questions_set: list[dict[str, list[str]]]) -> None:
    self.hero: 'Hero' = hero
    self.enemy: 'Character' = enemy
    self.active: bool = True
    self.current_question: str | None = None
    self.current_answer: str | None = None
    self.current_type: str | None = None
    self._last_question: str | None = None
    self.questions_set = questions_set if questions_set is not None else []

  def generate_question(self) -> str:
    """Generates a new word ordering grammar question."""
    questions = self.questions_set
    if not questions:
      self.current_question = None
      self.current_answer = None
      return ""
    # Evita repetir la última pregunta
    same_question = True
    while same_question:
      words, answer = random.choice(questions)
      shuffled_words = list(words)
      random.shuffle(shuffled_words)
      question_str = " / ".join(shuffled_words)
      if question_str != self._last_question:
        same_question = False
    self.current_question = question_str
    self.current_answer = answer
    self.current_type = "word_ordering"
    self._last_question = question_str
    return self.current_question

  def check_answer(self, player_answer: str) -> bool:
    """Checks if the player's answer is correct."""
    return player_answer.strip().lower() == self.current_answer.strip().lower()

  def process_turn(self, player_answer: str) -> str:
    """Process the turn based on player's answer. If both survive, generate a new question."""
    if not self.active or self.hero.dead or self.enemy.dead:
      """No hay combate activo."""
      pass
    if self.check_answer(player_answer):
      self.hero.attack(self.enemy)
      result = "¡Correcto! Atacas al enemigo."
    else:
      self.enemy.attack(self.hero)
      result = "Incorrecto. El enemigo te ataca."
    # Finaliza combate si alguno muere
    if self.enemy.dead or self.hero.dead:
      self.active = False
    else:
      self.generate_question()
    return result
