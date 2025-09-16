import pygame
from abc import ABC, abstractmethod


class Character(ABC):
  """Base class for all characters in the game."""

  def __init__(self, name, health, attack_power, image_path, x=0, y=0,
      sprites=None):
    self.name = name
    self.health = health
    self.attack_power = attack_power
    self.image = image_path
    self.x = x
    self.y = y
    self.sprites = sprites if sprites is not None else {}
    self.walking_sprites = []
    self.walk_index = 0
    self.walk_frame_count = 0
    self.walk_frame_delay_normal = 5  # Valor normal
    self.walk_frame_delay_border = 20  # Valor lento en el borde
    self.walk_frame_delay = self.walk_frame_delay_normal
    self.last_horizontal_direction = 1  # 1 = derecha, -1 = izquierda

  def is_alive(self):
    """Check if the character is alive."""
    return self.health > 0

  def attack(self, other):
    """Attack another character."""
    other.health -= self.attack_power
    print(f"{self.name} attacks {other.name} for {self.attack_power} damage!")

  def __str__(self):
    return f"{self.name}: {self.health} HP"

  def move(self, dx, dy, moving=False, window_width=640, window_height=480):
    """Move the character by (dx, dy). 'window_width' and 'window_height' define the screen boundaries."""
    prev_x, prev_y = self.x, self.y
    self.x += dx
    self.y += dy
    sprite_width = self.image.get_width()
    sprite_height = self.image.get_height()
    # Limita la posición para que no salga de la pantalla
    self.x = max(0, min(self.x, window_width - sprite_width))
    self.y = max(0, min(self.y, window_height - sprite_height))
    # Detecta si está en el borde
    at_border = (
        self.x == 0 or self.x == window_width - sprite_width or
        self.y == 0 or self.y == window_height - sprite_height
    )
    self.walk_frame_delay = self.walk_frame_delay_border if at_border else self.walk_frame_delay_normal

    if moving:
      self.walk_frame_count += 1
      # Actualiza la última dirección horizontal si hay movimiento horizontal
      if dx > 0:
        self.last_horizontal_direction = 1
      elif dx < 0:
        self.last_horizontal_direction = -1
      if self.walk_frame_count >= self.walk_frame_delay:
        self.walk_index = (self.walk_index + 1) % len(self.walking_sprites)
        self.walk_frame_count = 0
      sprite = self.walking_sprites[self.walk_index]
      # Refleja el sprite según la última dirección horizontal
      if self.last_horizontal_direction == 1:
        self.image = pygame.transform.flip(sprite, True, False)
      else:
        self.image = sprite
    else:
      # Si no se mueve, muestra el sprite base
      base_sprite = self.sprites["base"]
      if self.last_horizontal_direction == 1:
        self.image = pygame.transform.flip(base_sprite, True, False)
      else:
        self.image = base_sprite

  @abstractmethod
  def draw(self, surface):
    pass


class Hero(Character):
  def __init__(self, x=0, y=0):
    from Sprite.Characters import HERO_SPRITES
    super().__init__("Hero", 100, 10, HERO_SPRITES["base"], x, y, HERO_SPRITES)
    self.walking_sprites = [
      self.sprites["walking_1"],
      self.sprites["walking_2"],
      self.sprites["walking_3"]
    ]

  def draw(self, surface):
    surface.blit(self.image, (self.x, self.y))
