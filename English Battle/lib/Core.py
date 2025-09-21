"""Core module for the game, defining characters and their behaviors."""

from abc import ABC, abstractmethod

import pygame
import random
from pygame import Surface
from pygame.mixer import SoundType

from lib.Level import Level
from Sound import SOUNDS
from lib.Var import (
  DEFAULT_CHARACTER_SIZE,
  WALK_FRAME_DELAY_NORMAL,
  WALK_FRAME_DELAY_BORDER,
  DAMAGE_DISPLAY_FRAMES,
  ATTACK_DISPLAY_FRAMES,
)
from lib.Color import Color


class Character(ABC):
  """Base class for all characters in the game."""

  def __init__(self, name: str, health: int, attack_power: int,
      image_path: Surface, x: int = 0, y: int = 0,
      sprites: dict[str, Surface] = None, speed: int = 5,
      attack_range: int = 30, attack_cooldown: int = 30,
      attack_hit_sounds: list[SoundType] = None,
      attack_miss_sounds: list[SoundType] = None) -> None:
    # Base attributes
    self.name = name
    self.health = health
    self.max_health = health
    self.attack_power = attack_power
    self.speed = speed
    self.attack_range = attack_range
    # Position and image
    self.x = x
    self.y = y
    self.image = pygame.transform.scale(image_path, DEFAULT_CHARACTER_SIZE)
    self.sprites = {}
    if sprites is not None:
      for key, sprite in sprites.items():
        self.sprites[key] = pygame.transform.scale(sprite,
                                                   DEFAULT_CHARACTER_SIZE)
    else:
      self.sprites = {}
    # Walking animation
    self.walking_sprites = []
    self.walk_index = 0
    self.walk_frame_count = 0
    self.walk_frame_delay_normal = WALK_FRAME_DELAY_NORMAL
    self.walk_frame_delay_border = WALK_FRAME_DELAY_BORDER
    self.walk_frame_delay = self.walk_frame_delay_normal
    self.last_horizontal_direction = 1
    self.damage_timer = 0
    self.DAMAGE_DISPLAY_FRAMES = DAMAGE_DISPLAY_FRAMES
    # Attack management
    self.attack_timer = 0
    self.ATTACK_DISPLAY_FRAMES = ATTACK_DISPLAY_FRAMES
    self.attack_cooldown = attack_cooldown
    self.attack_cooldown_timer = 0
    # Sounds and step management
    self.step_sounds = None
    self.step_channel = None
    self.attack_hit_sounds = attack_hit_sounds if attack_hit_sounds else []
    self.attack_miss_sounds = attack_miss_sounds if attack_miss_sounds else []

  def is_alive(self) -> bool:
    """Check if the character is alive."""
    return self.health > 0

  def receive_damage(self, amount: int) -> None:
    """Receives damage and updates the sprite accordingly."""
    if not self.is_alive():
      return
    self.health -= amount
    if not self.is_alive():
      if isinstance(self, Hero) and "dead" in self.sprites:
        dead_sprite = self.sprites["dead"]
        new_size = (DEFAULT_CHARACTER_SIZE[1], DEFAULT_CHARACTER_SIZE[0])
        self.image = pygame.transform.scale(dead_sprite, new_size)
      else:
        self.image = self.sprites.get("dead", self.image)
    else:
      self.image = self.sprites.get("damage", self.image)
      self.damage_timer = self.DAMAGE_DISPLAY_FRAMES

  def update_sprite_after_damage(self) -> None:
    """Updates the sprite after damage timer expires."""
    if not self.is_alive():
      self._set_dead_sprite()
      return
    if self.attack_timer > 0:
      self._handle_attack_timer()
      return
    if self.damage_timer > 0:
      self._handle_damage_timer()
    self._handle_attack_cooldown_timer()

  def _set_dead_sprite(self) -> None:
    self.image = self.sprites.get("dead", self.image)

  def _handle_attack_timer(self) -> None:
    self.attack_timer -= 1
    if self.attack_timer == 0:
      base_sprite = self.sprites.get("base", self.image)
      if self.last_horizontal_direction == 1:
        self.image = pygame.transform.flip(base_sprite, True, False)
      else:
        self.image = base_sprite

  def _handle_damage_timer(self) -> None:
    self.damage_timer -= 1
    if self.damage_timer == 0:
      base_sprite = self.sprites.get("base", self.image)
      if self.last_horizontal_direction == 1:
        self.image = pygame.transform.flip(base_sprite, True, False)
      else:
        self.image = base_sprite

  def _handle_attack_cooldown_timer(self) -> None:
    if self.attack_cooldown_timer > 0:
      self.attack_cooldown_timer -= 1

  def can_attack(self, other: 'Character') -> bool:
    """Check if this character can attack another based on distance."""
    self_center = (
      self.x + DEFAULT_CHARACTER_SIZE[0] // 2,
      self.y + DEFAULT_CHARACTER_SIZE[1] // 2
    )
    other_center = (
      other.x + DEFAULT_CHARACTER_SIZE[0] // 2,
      other.y + DEFAULT_CHARACTER_SIZE[1] // 2
    )
    dist = ((self_center[0] - other_center[0]) ** 2 +
            (self_center[1] - other_center[1]) ** 2) ** 0.5
    return dist <= self.attack_range

  def attack(self, other: 'Character') -> None:
    """Attack another character if within range and cooldown expired. Play hit/miss sound."""
    if not self.is_alive() or not other.is_alive():
      return
    if self.attack_cooldown_timer > 0:
      return
    self.animate_attack()
    self.attack_timer = self.ATTACK_DISPLAY_FRAMES
    self.attack_cooldown_timer = self.attack_cooldown
    if self.can_attack(other):
      other.receive_damage(self.attack_power)
      if self.attack_hit_sounds:
        hit_sound = random.choice(self.attack_hit_sounds)
        if hit_sound:
          hit_sound.play()
      print(f"{self.name} attacks {other.name} for {self.attack_power} damage!")
    else:
      if self.attack_miss_sounds:
        miss_sound = random.choice(self.attack_miss_sounds)
        if miss_sound:
          miss_sound.play()

  def animate_attack(self) -> None:
    attack_sprite = self.sprites.get("attack", self.image)
    if self.last_horizontal_direction == 1:
      self.image = pygame.transform.flip(attack_sprite, True, False)
    else:
      self.image = attack_sprite

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
        if other is not self and other.is_alive() and future_rect_x.colliderect(
            pygame.Rect(other.x, other.y, sprite_width, sprite_height)):
          # Colisión con otro personaje vivo
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
        if other is not self and other.is_alive() and future_rect_y.colliderect(
            pygame.Rect(other.x, other.y, sprite_width, sprite_height)):
          return
    if dy != 0:
      self.y = new_y

  def move(self, dx: int, dy: int, moving: bool = False,
      window_width: int = 640, window_height: int = 480,
      level: Level = None, other_characters: list['Character'] = None) -> None:
    """Move the character by (dx, dy), handling collisions and updating sprite."""
    if not self.is_alive():
      return
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
      self._handle_walking_animation(dx)
    else:
      self._set_base_sprite()
    self.update_sprite_after_damage()

  def _handle_walking_animation(self, dx: int) -> None:
    self.walk_frame_count += 1
    if dx > 0:
      self.last_horizontal_direction = 1
    elif dx < 0:
      self.last_horizontal_direction = -1
    if self.walk_frame_count >= self.walk_frame_delay:
      self.walk_index = (self.walk_index + 1) % len(self.walking_sprites)
      self.walk_frame_count = 0
      if self.step_sounds:
        step_sound = random.choice(self.step_sounds)
        if step_sound and not self.step_channel.get_busy():
          self.step_channel.play(step_sound)
    sprite = self.walking_sprites[self.walk_index]
    if self.last_horizontal_direction == 1:
      self.image = pygame.transform.flip(sprite, True, False)
    else:
      self.image = sprite

  def _set_base_sprite(self) -> None:
    base_sprite = self.sprites["base"]
    if self.last_horizontal_direction == 1:
      self.image = pygame.transform.flip(base_sprite, True, False)
    else:
      self.image = base_sprite

  def draw_health_bar(self, surface: Surface) -> None:
    """
    Draws the health bar above the character.
    """
    bar_width = DEFAULT_CHARACTER_SIZE[0]
    bar_height = 6
    x = self.x
    y = self.y - bar_height - 2
    health_ratio = max(0,
                       self.health) / self.max_health if self.max_health > 0 else 0
    fill_width = int(bar_width * health_ratio)
    # Background
    pygame.draw.rect(surface, Color.HEALTH_BAR_BG,
                     (x, y, bar_width, bar_height))
    # Health bar (green/red)
    color = Color.HEALTH_BAR_GREEN if health_ratio > 0.3 else Color.HEALTH_BAR_RED
    pygame.draw.rect(surface, color, (x, y, fill_width, bar_height))
    # Border
    pygame.draw.rect(surface, Color.HEALTH_BAR_BORDER,
                     (x, y, bar_width, bar_height), 1)

  def draw(self, surface: Surface) -> None:
    """
    Draws the zombie and its health bar on the given surface.
    """
    surface.blit(self.image, (self.x, self.y))
    self.draw_health_bar(surface)


class Hero(Character):
  """Class representing the hero character."""

  def __init__(self, x: int = 0, y: int = 0, health: int = 100) -> None:
    from Sprite.Characters import HERO_SPRITES
    from Sound import SOUNDS
    super().__init__(
        "Hero", health, 10, HERO_SPRITES["base"], x, y, HERO_SPRITES,
        speed=2, attack_range=30, attack_cooldown=20,
        attack_hit_sounds=[
          SOUNDS.get("cbar_hitbod2")
        ],
        attack_miss_sounds=[
          SOUNDS.get("cbar_miss1")
        ]
    )
    self.walking_sprites = [
      self.sprites["walking_1"],
      self.sprites["walking_2"],
      self.sprites["walking_3"],
      self.sprites["walking_4"]
    ]
    self.step_sounds = [
      SOUNDS.get("pl_step1"),
      SOUNDS.get("pl_step2"),
      SOUNDS.get("pl_step3"),
      SOUNDS.get("pl_step4")
    ]
    self.step_channel = pygame.mixer.Channel(5)


class Zombie(Character):
  """Class representing a zombie enemy."""

  def __init__(self, x: int = 0, y: int = 0, health: int = 10) -> None:
    from Sprite.Enemies import ZOMBIE_SPRITES
    super().__init__("Zombie", health, 10, ZOMBIE_SPRITES["base"], x, y,
                     ZOMBIE_SPRITES, speed=1, attack_range=30,
                     attack_cooldown=60,
                     attack_hit_sounds=[
                       SOUNDS.get("claw_strike1"), SOUNDS.get("claw_strike2"),
                       SOUNDS.get("claw_strike3")
                     ],
                     attack_miss_sounds=[
                       SOUNDS.get("cbar_miss1")
                     ])
    self.walking_sprites = [
      self.sprites["walking_1"],
      self.sprites["walking_2"],
      self.sprites["walking_3"]
    ]
    self.step_sounds = []
    self.walk_frame_delay_normal = WALK_FRAME_DELAY_NORMAL
    self.walk_frame_delay_border = WALK_FRAME_DELAY_BORDER
