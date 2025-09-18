"""Module for generating and managing maze levels in a game."""

from pygame import Rect, Surface

from Sprite.Backgrounds import BACKGROUNDS
import pygame
import random


def random_maze_walls(window_size: tuple[int, int], num_walls: int = 6,
    min_size: int = 40,
    max_size: int = 200) -> list[Rect]:
  """Generates random walls for a maze."""
  walls = []
  w, h = window_size
  for _ in range(num_walls):
    wall_width = random.randint(min_size, max_size)
    wall_height = random.randint(15, 30)
    x = random.randint(0, w - wall_width)
    y = random.randint(0, h - wall_height)
    walls.append(pygame.Rect(x, y, wall_width, wall_height))
  return walls


def generate_simple_maze(window_size: tuple[int, int], wall_thickness: int = 20,
    cell_size: int = 80) -> list[Rect]:
  """Generates a simple grid maze without gaps."""
  walls = []
  w, h = window_size
  # Paredes verticales
  for x in range(cell_size, w, cell_size):
    for y in range(0, h, cell_size):
      walls.append(pygame.Rect(x, y, wall_thickness, cell_size))
  # Paredes horizontales
  for y in range(cell_size, h, cell_size):
    for x in range(0, w, cell_size):
      walls.append(pygame.Rect(x, y, cell_size, wall_thickness))
  # Bordes del laberinto
  walls.append(pygame.Rect(0, 0, w, wall_thickness))  # superior
  walls.append(
      pygame.Rect(0, h - wall_thickness, w, wall_thickness))  # inferior
  walls.append(pygame.Rect(0, 0, wall_thickness, h))  # izquierdo
  walls.append(pygame.Rect(w - wall_thickness, 0, wall_thickness, h))  # derecho
  return walls


def generate_grid_maze_with_gaps(window_size: tuple[int, int],
    wall_thickness: int = 20,
    cell_size: int = 80) -> list[Rect]:
  """Genera un laberinto grid con huecos (puertas) en las paredes para permitir movimiento."""
  walls = []
  w, h = window_size
  # Paredes verticales con huecos
  for x in range(cell_size, w, cell_size):
    for y in range(0, h, cell_size):
      # Deja huecos en algunas celdas
      if (y // cell_size) % 2 == 0:
        continue
      walls.append(pygame.Rect(x, y, wall_thickness, cell_size))
  # Paredes horizontales con huecos
  for y in range(cell_size, h, cell_size):
    for x in range(0, w, cell_size):
      if (x // cell_size) % 2 == 1:
        continue
      walls.append(pygame.Rect(x, y, cell_size, wall_thickness))
  # Bordes del laberinto, pero deja una "puerta" arriba y abajo
  gap_size = cell_size
  # Superior
  walls.append(pygame.Rect(0, 0, w // 2 - gap_size // 2, wall_thickness))
  walls.append(pygame.Rect(w // 2 + gap_size // 2, 0, w // 2 - gap_size // 2,
                           wall_thickness))
  # Inferior
  walls.append(
      pygame.Rect(0, h - wall_thickness, w // 2 - gap_size // 2,
                  wall_thickness))
  walls.append(pygame.Rect(w // 2 + gap_size // 2, h - wall_thickness,
                           w // 2 - gap_size // 2, wall_thickness))
  # Izquierdo
  walls.append(pygame.Rect(0, 0, wall_thickness, h // 2 - gap_size // 2))
  walls.append(pygame.Rect(0, h // 2 + gap_size // 2, wall_thickness,
                           h // 2 - gap_size // 2))
  # Derecho
  walls.append(
      pygame.Rect(w - wall_thickness, 0, wall_thickness,
                  h // 2 - gap_size // 2))
  walls.append(
      pygame.Rect(w - wall_thickness, h // 2 + gap_size // 2, wall_thickness,
                  h // 2 - gap_size // 2))
  return walls


def init_maze_structures(cols: int, rows: int) -> tuple[
  list[list[bool]], list[list[bool]], list[list[bool]]]:
  """Initializes the structures for maze generation."""
  visited = [[False for _ in range(rows)] for _ in range(cols)]
  vertical_walls = [[True for _ in range(rows)] for _ in range(cols + 1)]
  horizontal_walls = [[True for _ in range(rows + 1)] for _ in range(cols)]
  return visited, vertical_walls, horizontal_walls


def dfs_maze(cx: int, cy: int, cols: int, rows: int, visited: list[list[bool]],
    vertical_walls: list[list[int]], horizontal_walls: list[list[int]]) -> None:
  """Depth-First Search maze generation algorithm."""
  visited[cx][cy] = True
  directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
  random.shuffle(directions)
  for dx, dy in directions:
    nx, ny = cx + dx, cy + dy
    if 0 <= nx < cols and 0 <= ny < rows and not visited[nx][ny]:
      if dx == 1:  # derecha
        vertical_walls[cx + 1][cy] = False
      if dx == -1:  # izquierda
        vertical_walls[cx][cy] = False
      if dy == 1:  # abajo
        horizontal_walls[cx][cy + 1] = False
      if dy == -1:  # arriba
        horizontal_walls[cx][cy] = False
      dfs_maze(nx, ny, cols, rows, visited, vertical_walls, horizontal_walls)


def build_maze_walls(cols: int, rows: int, cell_size: int, wall_thickness: int,
    window_size: tuple[int, int],
    vertical_walls: list[list[int]], horizontal_walls: list[list[int]]) -> list[
  Rect]:
  """Builds the maze walls from the wall structures."""
  w, h = window_size
  walls = []
  # Construye las paredes verticales
  for x in range(cols + 1):
    for y in range(rows):
      if vertical_walls[x][y]:
        wx = x * cell_size
        wy = y * cell_size
        walls.append(pygame.Rect(wx, wy, wall_thickness, cell_size))
  # Construye las paredes horizontales
  for x in range(cols):
    for y in range(rows + 1):
      if horizontal_walls[x][y]:
        wx = x * cell_size
        wy = y * cell_size
        walls.append(pygame.Rect(wx, wy, cell_size, wall_thickness))
  # Bordes del laberinto
  walls.append(pygame.Rect(0, 0, w, wall_thickness))  # superior
  walls.append(
      pygame.Rect(0, h - wall_thickness, w, wall_thickness))  # inferior
  walls.append(pygame.Rect(0, 0, wall_thickness, h))  # izquierdo
  walls.append(pygame.Rect(w - wall_thickness, 0, wall_thickness, h))  # derecho
  return walls


def generate_random_maze(window_size: tuple[int, int], wall_thickness: int = 20,
    cell_size: int = 80) -> list[Rect]:
  """Generates a random maze using DFS algorithm."""
  w, h = window_size
  cols = w // cell_size
  rows = h // cell_size

  visited, vertical_walls, horizontal_walls = init_maze_structures(cols, rows)
  start_x = random.randint(0, cols - 1)
  start_y = random.randint(0, rows - 1)
  dfs_maze(start_x, start_y, cols, rows, visited, vertical_walls,
           horizontal_walls)
  walls = build_maze_walls(cols, rows, cell_size, wall_thickness, window_size,
                           vertical_walls, horizontal_walls)
  return walls


class Level:
  """Class to manage the game level, including background and maze."""

  def __init__(self, window_size: tuple[int, int] = (640, 480),
      background_name: str = "grass") -> None:
    self.window_size = window_size
    self.background_name = background_name
    self.background = pygame.transform.scale(
        BACKGROUNDS[self.background_name], self.window_size
    )
    self.maze_walls = generate_random_maze(self.window_size)

  def draw_background(self, surface: Surface) -> None:
    surface.blit(self.background, (0, 0))

  def draw_maze(self, surface: Surface) -> None:
    for wall in self.maze_walls:
      pygame.draw.rect(surface, (80, 80, 80), wall)

  def check_collision(self, rect: Rect) -> bool:
    """Devuelve True si rect colisiona con alguna pared del laberinto."""
    for wall in self.maze_walls:
      if rect.colliderect(wall):
        return True
    return False
