"""Core module for the game, defining characters and their behaviors."""

from abc import ABC, abstractmethod

import pygame
import random
from pygame import Surface

from lib.Level import Level
from Sound import SOUNDS

DEFAULT_CHARACTER_SIZE = (23, 30)


class Character(ABC):
  """Base class for all characters in the game."""

  def __init__(self, name: str, health: int, attack_power: int,
      image_path: Surface, x: int = 0, y: int = 0,
      sprites: dict[str, Surface] = None, speed: int = 5,
      attack_range: int = 30, attack_cooldown: int = 30) -> None:
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
    self.attack_range = attack_range
    self.dead = False
    self.damage_timer = 0
    self.DAMAGE_DISPLAY_FRAMES = 15  # frames para mostrar sprite de daño
    self.attack_timer = 0
    self.ATTACK_DISPLAY_FRAMES = 10  # frames para mostrar sprite de ataque
    self.attack_cooldown = attack_cooldown  # frames de cooldown
    self.attack_cooldown_timer = 0  # frames restantes para poder atacar

  def is_alive(self) -> bool:
    """Check if the character is alive."""
    return self.health > 0

  def receive_damage(self, amount: int) -> None:
    """Receives damage and updates the sprite accordingly."""
    if self.dead:
      return
    self.health -= amount
    if self.health <= 0:
      self.dead = True
      self.image = self.sprites.get("dead", self.image)
    else:
      self.image = self.sprites.get("damage", self.image)
      self.damage_timer = self.DAMAGE_DISPLAY_FRAMES

  def update_sprite_after_damage(self) -> None:
    """Updates the sprite after damage timer expires."""
    if self.dead:
      self.image = self.sprites.get("dead", self.image)
      return
    if self.attack_timer > 0:
      self.attack_timer -= 1
      if self.attack_timer == 0:
        base_sprite = self.sprites.get("base", self.image)
        if self.last_horizontal_direction == 1:
          self.image = pygame.transform.flip(base_sprite, True, False)
        else:
          self.image = base_sprite
      return
    if self.damage_timer > 0:
      self.damage_timer -= 1
      if self.damage_timer == 0:
        base_sprite = self.sprites.get("base", self.image)
        if self.last_horizontal_direction == 1:
          self.image = pygame.transform.flip(base_sprite, True, False)
        else:
          self.image = base_sprite
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
    """Attack another character if within range and cooldown expired."""
    if self.dead or other.dead:
      return
    if self.attack_cooldown_timer > 0:
      return
    attack_sprite = self.sprites.get("attack", self.image)
    if self.last_horizontal_direction == 1:
      self.image = pygame.transform.flip(attack_sprite, True, False)
    else:
      self.image = attack_sprite
    self.attack_timer = self.ATTACK_DISPLAY_FRAMES
    self.attack_cooldown_timer = self.attack_cooldown
    if self.can_attack(other):
      other.receive_damage(self.attack_power)
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
        if other is not self and not other.dead and future_rect_x.colliderect(
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
        if other is not self and not other.dead and future_rect_y.colliderect(
            pygame.Rect(other.x, other.y, sprite_width, sprite_height)):
          return
    if dy != 0:
      self.y = new_y

  def move(self, dx: int, dy: int, moving: bool = False,
      window_width: int = 640, window_height: int = 480,
      level: Level = None, other_characters: list['Character'] = None) -> None:
    """Move the character by (dx, dy), handling collisions and updating sprite."""
    if self.dead:
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
      self.walk_frame_count += 1
      if dx > 0:
        self.last_horizontal_direction = 1
      elif dx < 0:
        self.last_horizontal_direction = -1
      if self.walk_frame_count >= self.walk_frame_delay:
        prev_walk_index = self.walk_index
        self.walk_index = (self.walk_index + 1) % len(self.walking_sprites)
        self.walk_frame_count = 0
        # Selecciona aleatoriamente el sonido de paso
        if self.step_sounds:
          step_sound = random.choice(self.step_sounds)
          if step_sound and not self.step_channel.get_busy():
            self.step_channel.play(step_sound)
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
    self.update_sprite_after_damage()

  @abstractmethod
  def draw(self, surface: Surface) -> None:
    """Draw the character on the given surface."""
    pass


class Hero(Character):
  """Class representing the hero character."""

  def __init__(self, x: int = 0, y: int = 0) -> None:
    from Sprite.Characters import HERO_SPRITES
    super().__init__("Hero", 100, 10, HERO_SPRITES["base"], x, y, HERO_SPRITES,
                     speed=2, attack_range=30,
                     attack_cooldown=20)  # Cooldown corto
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
    self.step_channel = pygame.mixer.Channel(5)  # Canal dedicado para pasos

  def attack(self, other: 'Character') -> None:
    """Attack another character if within range and cooldown expired. Play hit/miss sound."""
    if self.dead or other.dead:
      return
    if self.attack_cooldown_timer > 0:
      return
    attack_sprite = self.sprites.get("attack", self.image)
    if self.last_horizontal_direction == 1:
      self.image = pygame.transform.flip(attack_sprite, True, False)
    else:
      self.image = attack_sprite
    self.attack_timer = self.ATTACK_DISPLAY_FRAMES
    self.attack_cooldown_timer = self.attack_cooldown
    if self.can_attack(other):
      other.receive_damage(self.attack_power)
      hit_sound = SOUNDS.get("cbar_hitbod2")
      if hit_sound:
        hit_sound.play()
      print(f"{self.name} attacks {other.name} for {self.attack_power} damage!")
    else:
      miss_sound = SOUNDS.get("cbar_miss1")
      if miss_sound:
        miss_sound.play()

  def draw(self, surface: Surface) -> None:
    surface.blit(self.image, (self.x, self.y))


class Zombie(Character):
  """Class representing a zombie enemy."""

  def __init__(self, x: int = 0, y: int = 0) -> None:
    from Sprite.Enemies import ZOMBIE_SPRITES
    super().__init__("Zombie", 10, 10, ZOMBIE_SPRITES["base"], x, y,
                     ZOMBIE_SPRITES, speed=1, attack_range=30,
                     attack_cooldown=60)  # Cooldown largo
    self.walking_sprites = [
      self.sprites["walking_1"],
      self.sprites["walking_2"],
      self.sprites["walking_3"]
    ]
    self.step_sounds = []
    self.walk_frame_delay_normal = 15
    self.walk_frame_delay_border = 40

  def draw(self, surface: Surface) -> None:
    surface.blit(self.image, (self.x, self.y))
