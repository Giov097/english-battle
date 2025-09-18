"""Core module for the game, defining characters and their behaviors."""

from abc import ABC, abstractmethod

import pygame
from pygame import Surface

from lib.Level import Level

DEFAULT_CHARACTER_SIZE = (23, 30)


class Character(ABC):
  """Base class for all characters in the game."""

  def __init__(self, name: str, health: int, attack_power: int,
      image_path: Surface, x: int = 0, y: int = 0,
      sprites: dict[str, Surface] = None, speed: int = 5) -> None:
    self.name = name
    self.health = health
    self.attack_power = attack_power
    self.image = pygame.transform.scale(image_path, DEFAULT_CHARACTER_SIZE)
    self.x = x
    self.y = y
    self.sprites = {}
    if sprites is not None:
      for key, sprite in sprites.items():
        self.sprites[key] = pygame.transform.scale(sprite,
                                                   DEFAULT_CHARACTER_SIZE)
    else:
      self.sprites = {}
    self.walking_sprites = []
    self.walk_index = 0
    self.walk_frame_count = 0
    # Valor normal
    self.walk_frame_delay_normal = 5
    # Valor lento en el borde
    self.walk_frame_delay_border = 20
    self.walk_frame_delay = self.walk_frame_delay_normal
    # 1 derecha, -1 izquierda
    self.last_horizontal_direction = 1
    # Velocidad por defecto
    self.speed = speed

  def is_alive(self) -> bool:
    """Check if the character is alive."""
    return self.health > 0

  def attack(self, other: 'Character') -> None:
    """Attack another character."""
    other.health -= self.attack_power
    print(f"{self.name} attacks {other.name} for {self.attack_power} damage!")

  def __str__(self) -> str:
    return f"{self.name}: {self.health} HP"

  def __try_move_x__(self, dx: int, window_width: int, sprite_width: int,
      sprite_height: int, level: Level,
      other_characters: list['Character']) -> None:
    new_x = self.x + (dx * self.speed if dx != 0 else 0)
    new_x = max(0, min(new_x, window_width - sprite_width))
    future_rect_x = pygame.Rect(new_x, self.y, sprite_width, sprite_height)
    if level is not None and dx != 0 and level.check_collision(future_rect_x):
      # Colisión con laberinto
      return
    if other_characters is not None and dx != 0:
      for other in other_characters:
        if other is not self and future_rect_x.colliderect(
            pygame.Rect(other.x, other.y, sprite_width, sprite_height)):
          # Colisión con otro personaje
          return
    if dx != 0:
      self.x = new_x

  def __try_move_y__(self, dy: int, window_height: int, sprite_width: int,
      sprite_height: int, level: Level,
      other_characters: list['Character']) -> None:
    new_y = self.y + (dy * self.speed if dy != 0 else 0)
    new_y = max(0, min(new_y, window_height - sprite_height))
    future_rect_y = pygame.Rect(self.x, new_y, sprite_width, sprite_height)
    if level is not None and dy != 0 and level.check_collision(future_rect_y):
      # Colisión con laberinto
      return
    if other_characters is not None and dy != 0:
      for other in other_characters:
        if other is not self and future_rect_y.colliderect(
            pygame.Rect(other.x, other.y, sprite_width, sprite_height)):
          # Colisión con otro personaje
          return
    if dy != 0:
      self.y = new_y

  def move(self, dx: int, dy: int, moving: bool = False,
      window_width: int = 640, window_height: int = 480,
      level: Level = None, other_characters: list['Character'] = None) -> None:
    sprite_width = DEFAULT_CHARACTER_SIZE[0]
    sprite_height = DEFAULT_CHARACTER_SIZE[1]

    self.__try_move_x__(dx, window_width, sprite_width, sprite_height, level,
                        other_characters)
    self.__try_move_y__(dy, window_height, sprite_width, sprite_height, level,
                        other_characters)

    at_border = (
        self.x == 0 or self.x == window_width - sprite_width or
        self.y == 0 or self.y == window_height - sprite_height
    )
    self.walk_frame_delay = self.walk_frame_delay_border if at_border else self.walk_frame_delay_normal

    if moving:
      self.walk_frame_count += 1
      if dx > 0:
        self.last_horizontal_direction = 1
      elif dx < 0:
        self.last_horizontal_direction = -1
      if self.walk_frame_count >= self.walk_frame_delay:
        self.walk_index = (self.walk_index + 1) % len(self.walking_sprites)
        self.walk_frame_count = 0
      sprite = self.walking_sprites[self.walk_index]
      if self.last_horizontal_direction == 1:
        self.image = pygame.transform.flip(sprite, True, False)
      else:
        self.image = sprite
    else:
      base_sprite = self.sprites["base"]
      if self.last_horizontal_direction == 1:
        self.image = pygame.transform.flip(base_sprite, True, False)
      else:
        self.image = base_sprite

  @abstractmethod
  def draw(self, surface: Surface) -> None:
    """Draw the character on the given surface."""
    pass


class Hero(Character):
  """Class representing the hero character."""

  def __init__(self, x: int = 0, y: int = 0) -> None:
    from Sprite.Characters import HERO_SPRITES
    super().__init__("Hero", 100, 10, HERO_SPRITES["base"], x, y, HERO_SPRITES,
                     speed=2)
    self.walking_sprites = [
      self.sprites["walking_1"],
      self.sprites["walking_2"],
      self.sprites["walking_3"]
    ]

  def draw(self, surface: Surface) -> None:
    surface.blit(self.image, (self.x, self.y))


class Zombie(Character):
  """Class representing a zombie enemy."""

  def __init__(self, x: int = 0, y: int = 0) -> None:
    from Sprite.Enemies import ZOMBIE_SPRITES
    super().__init__("Zombie", 50, 10, ZOMBIE_SPRITES["base"], x, y,
                     ZOMBIE_SPRITES, speed=1)
    self.walking_sprites = [
      self.sprites["walking_1"],
      self.sprites["walking_2"],
      self.sprites["walking_3"]
    ]
    self.walk_frame_delay_normal = 15
    self.walk_frame_delay_border = 40

  def draw(self, surface: Surface) -> None:
    surface.blit(self.image, (self.x, self.y))
