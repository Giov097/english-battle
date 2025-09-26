"""Core module for the game, defining characters and their behaviors."""

import random
from abc import ABC

import pygame
from pygame import Surface
from pygame.mixer import SoundType

from Sound import SOUNDS
from lib.Color import Color
from lib.Level import Level
from lib.Var import Var


class Character(ABC):
  """Base class for all characters in the game."""

  def __init__(self, name: str, health: int, attack_power: int,
      image_path: Surface, x: int = 0, y: int = 0,
      sprites: dict[str, Surface] = None, speed: int = 5,
      attack_range: int = 30, attack_cooldown: int = 30,
      attack_hit_sounds: list[SoundType] = None,
      attack_miss_sounds: list[SoundType] = None) -> None:
    """
    Initializes a character with given attributes.
    :param name: character name
    :param health: maximum and initial health
    :param attack_power: damage dealt per attack
    :param image_path: initial image surface
    :param x: initial x position
    :param y: initial y position
    :param sprites: dictionary of character sprites
    :param speed: movement speed
    :param attack_range: range within which the character can attack
    :param attack_cooldown: frames between attacks
    :param attack_hit_sounds: list of sounds to play on successful hit
    :param attack_miss_sounds: list of sounds to play on missed attack
    """
    # Base attributes
    self.__name = name
    self.__health = health
    self.__max_health = health
    self.__attack_power = attack_power
    self.__speed = speed
    self.__attack_range = attack_range
    # Position and image
    self.__x = x
    self.__y = y
    self.__image = pygame.transform.scale(image_path,
                                          Var.DEFAULT_CHARACTER_SIZE)
    self.__sprites = {}
    if sprites is not None:
      for key, sprite in sprites.items():
        self.__sprites[key] = pygame.transform.scale(sprite,
                                                     Var.DEFAULT_CHARACTER_SIZE)
    else:
      self.__sprites = {}
    # Walking animation
    self.__walking_sprites = []
    self.__walk_index = 0
    self.__walk_frame_count = 0
    self.__walk_frame_delay_normal = Var.WALK_FRAME_DELAY_NORMAL
    self.__walk_frame_delay_border = Var.WALK_FRAME_DELAY_BORDER
    self.__walk_frame_delay = self.__walk_frame_delay_normal
    self.__last_horizontal_direction = 1
    self.__damage_timer = 0
    self.__DAMAGE_DISPLAY_FRAMES = Var.DAMAGE_DISPLAY_FRAMES
    # Attack management
    self.__attack_timer = 0
    self.__ATTACK_DISPLAY_FRAMES = Var.ATTACK_DISPLAY_FRAMES
    self.__attack_cooldown = attack_cooldown
    self.__attack_cooldown_timer = 0
    # Sounds and step management
    self.__step_sounds = None
    self.__step_channel = None
    self.__attack_hit_sounds = attack_hit_sounds if attack_hit_sounds else []
    self.__attack_miss_sounds = attack_miss_sounds if attack_miss_sounds else []

  def is_alive(self) -> bool:
    """
    Check if the character is alive.
    :return: True if health > 0, else False
    """
    return self.__health > 0

  def get_x(self) -> int:
    """
    Get the x-coordinate of the character.
    :return: x-coordinate
    """
    return self.__x

  def get_y(self) -> int:
    """
    Get the y-coordinate of the character.
    :return: y-coordinate
    """
    return self.__y

  def get_attack_range(self) -> int:
    """
    Get the attack range of the character.
    :return: attack range
    """
    return self.__attack_range

  def get_health(self) -> int:
    """
    Get the current health of the character.
    :return: current health
    """
    return self.__health

  def _set_health(self, health: int) -> None:
    """
    Set the current health of the character.
    :param health: new health value
    """
    self.__health = max(0, min(health, self.__max_health))
    if not self.is_alive():
      self._set_dead_sprite()

  def get_max_health(self) -> int:
    """
    Get the maximum health of the character.
    :return: maximum health
    """
    return self.__max_health

  def get_walk_index(self) -> int:
    """
    Get the current walk index for animation.
    :return: current walk index
    """
    return self.__walk_index

  def receive_damage(self, amount: int) -> None:
    """
    Receives damage and updates the sprite accordingly.
    :param amount: damage amount
    """
    if self.is_alive():
      self.__health -= amount
      if not self.is_alive():
        if isinstance(self, Hero) and "dead" in self.get_sprites():
          dead_sprite = self.get_sprites()["dead"]
          new_size = (Var.DEFAULT_CHARACTER_SIZE[1],
                      Var.DEFAULT_CHARACTER_SIZE[0])
          self.__image = pygame.transform.scale(dead_sprite, new_size)
        else:
          self.__image = self.__sprites.get("dead", self.__image)
      else:
        self.__image = self.__sprites.get("damage", self.__image)
        self.__damage_timer = self.__DAMAGE_DISPLAY_FRAMES

  def update_sprite_after_damage(self) -> None:
    """
    Updates the sprite after damage timer expires.
    """
    if not self.is_alive():
      self._set_dead_sprite()
      return
    if self.__attack_timer > 0:
      self._handle_attack_timer()
      return
    if self.__damage_timer > 0:
      self._handle_damage_timer()
    self._handle_attack_cooldown_timer()

  def _set_dead_sprite(self) -> None:
    """
    Set the dead sprite when the character dies.
    """
    self.__image = self.__sprites.get("dead", self.__image)

  def _handle_attack_timer(self) -> None:
    """
    Handle the attack timer and reset sprite after attack animation.
    """
    self.__attack_timer -= 1
    if self.__attack_timer == 0:
      base_sprite = self.__sprites.get("base", self.__image)
      if self.__last_horizontal_direction == 1:
        self.__image = pygame.transform.flip(base_sprite, True, False)
      else:
        self.__image = base_sprite

  def _handle_damage_timer(self) -> None:
    """
    Handle the damage timer and reset sprite after damage animation.
    """
    self.__damage_timer -= 1
    if self.__damage_timer == 0:
      base_sprite = self.__sprites.get("base", self.__image)
      if self.__last_horizontal_direction == 1:
        self.__image = pygame.transform.flip(base_sprite, True, False)
      else:
        self.__image = base_sprite

  def _handle_attack_cooldown_timer(self) -> None:
    """
    Handle the attack cooldown timer.
    """
    if self.__attack_cooldown_timer > 0:
      self.__attack_cooldown_timer -= 1

  def can_attack(self, other: 'Character') -> bool:
    """
    Check if this character can attack another based on distance.
    :param other: another character
    :return: True if within attack range, else False
    """
    self_center = (
      self.__x + Var.DEFAULT_CHARACTER_SIZE[0] // 2,
      self.__y + Var.DEFAULT_CHARACTER_SIZE[1] // 2
    )
    other_center = (
      other.__x + Var.DEFAULT_CHARACTER_SIZE[0] // 2,
      other.__y + Var.DEFAULT_CHARACTER_SIZE[1] // 2
    )
    dist = ((self_center[0] - other_center[0]) ** 2 +
            (self_center[1] - other_center[1]) ** 2) ** 0.5
    return dist <= self.__attack_range

  def attack(self, other: 'Character') -> None:
    """
    Attack another character if within range and cooldown expired. Play hit/miss sound.
    :param other: another character to attack
    """
    if not self.is_alive() or not other.is_alive():
      return
    if self.__attack_cooldown_timer > 0:
      return
    self.animate_attack()
    self.__attack_timer = self.__ATTACK_DISPLAY_FRAMES
    self.__attack_cooldown_timer = self.__attack_cooldown
    if self.can_attack(other):
      other.receive_damage(self.__attack_power)
      if self.__attack_hit_sounds:
        hit_sound = random.choice(self.__attack_hit_sounds)
        if hit_sound:
          hit_sound.play()
      print(
          f"{self.__name} attacks {other.__name} for {self.__attack_power} damage!")
    else:
      if self.__attack_miss_sounds:
        miss_sound = random.choice(self.__attack_miss_sounds)
        if miss_sound:
          miss_sound.play()

  def animate_attack(self) -> None:
    """
    Change the sprite to the attack sprite during an attack.
    """
    attack_sprite = self.__sprites.get("attack", self.__image)
    if self.__last_horizontal_direction == 1:
      self.__image = pygame.transform.flip(attack_sprite, True, False)
    else:
      self.__image = attack_sprite

  def __str__(self) -> str:
    """
    String representation of the character.
    :return: character name and current health
    """
    return f"{self.__name}: {self.__health} HP"

  def __try_move_x__(self, dx: int, window_width: int, sprite_width: int,
      sprite_height: int, level: Level,
      other_characters: list['Character']) -> None:
    """
    Attempt to move the character in the x direction, handling collisions.
    :param dx: change in x direction (-1, 0, 1)
    :param window_width: width of the game window
    :param sprite_width: width of the character sprite
    :param sprite_height: height of the character sprite
    :param level: current game level for collision detection
    :param other_characters: list of other characters for collision detection
    """
    new_x = self.__x + (dx * self.__speed if dx != 0 else 0)
    new_x = max(0, min(new_x, window_width - sprite_width))
    future_rect_x = pygame.Rect(new_x, self.__y, sprite_width, sprite_height)
    if level is not None and dx != 0 and level.check_collision(future_rect_x):
      # Colisión con laberinto
      return
    if other_characters is not None and dx != 0:
      for other in other_characters:
        if other is not self and other.is_alive() and future_rect_x.colliderect(
            pygame.Rect(other.__x, other.__y, sprite_width, sprite_height)):
          return
    if dx != 0:
      self.__x = new_x

  def __try_move_y__(self, dy: int, window_height: int, sprite_width: int,
      sprite_height: int, level: Level,
      other_characters: list['Character']) -> None:
    """
    Attempt to move the character in the y direction, handling collisions.
    :param dy: change in y direction (-1, 0, 1)
    :param window_height: height of the game window
    :param sprite_width: width of the character sprite
    :param sprite_height: height of the character sprite
    :param level: current game level for collision detection
    :param other_characters: list of other characters for collision detection
    """
    new_y = self.__y + (dy * self.__speed if dy != 0 else 0)
    new_y = max(0, min(new_y, window_height - sprite_height))
    future_rect_y = pygame.Rect(self.__x, new_y, sprite_width, sprite_height)
    if level is not None and dy != 0 and level.check_collision(future_rect_y):
      # Colisión con laberinto
      return
    if other_characters is not None and dy != 0:
      for other in other_characters:
        if other is not self and other.is_alive() and future_rect_y.colliderect(
            pygame.Rect(other.__x, other.__y, sprite_width, sprite_height)):
          return
    if dy != 0:
      self.__y = new_y

  def move(self, dx: int, dy: int, moving: bool = False,
      window_width: int = 640, window_height: int = 480,
      level: Level = None, other_characters: list['Character'] = None) -> None:
    """
    Move the character by (dx, dy), handling collisions and updating sprite.
    :param dx: change in x direction (-1, 0, 1)
    :param dy: change in y direction (-1, 0, 1)
    :param moving: whether the character is currently moving
    :param window_width: width of the game window
    :param window_height: height of the game window
    :param level: current game level for collision detection
    :param other_characters: list of other characters for collision detection
    """
    if self.is_alive():
      sprite_width = Var.DEFAULT_CHARACTER_SIZE[0]
      sprite_height = Var.DEFAULT_CHARACTER_SIZE[1]

      self.__try_move_x__(dx, window_width, sprite_width, sprite_height, level,
                          other_characters)
      self.__try_move_y__(dy, window_height, sprite_width, sprite_height, level,
                          other_characters)

      at_border = (
          self.__x == 0 or self.__x == window_width - sprite_width or
          self.__y == 0 or self.__y == window_height - sprite_height
      )
      self.__walk_frame_delay = self.__walk_frame_delay_border if at_border else self.__walk_frame_delay_normal

      if moving:
        self._handle_walking_animation(dx)
      else:
        self._set_base_sprite()
      self.update_sprite_after_damage()

  def _handle_walking_animation(self, dx: int) -> None:
    """
    Update walking animation based on movement direction and frame count.
    :param dx:
    """
    self.__walk_frame_count += 1
    if dx > 0:
      self.__last_horizontal_direction = 1
    elif dx < 0:
      self.__last_horizontal_direction = -1
    if self.__walk_frame_count >= self.__walk_frame_delay:
      self.__walk_index = (self.__walk_index + 1) % len(self.__walking_sprites)
      self.__walk_frame_count = 0
      if self.__step_sounds:
        step_sound = random.choice(self.__step_sounds)
        if step_sound and not self.__step_channel.get_busy():
          self.__step_channel.play(step_sound)
    sprite = self.__walking_sprites[self.get_walk_index()]
    if self.__last_horizontal_direction == 1:
      self.__image = pygame.transform.flip(sprite, True, False)
    else:
      self.__image = sprite

  def _set_base_sprite(self) -> None:
    """
    Set the character's sprite to the base sprite.
    """
    base_sprite = self.__sprites["base"]
    if self.__last_horizontal_direction == 1:
      self.__image = pygame.transform.flip(base_sprite, True, False)
    else:
      self.__image = base_sprite

  def draw_health_bar(self, surface: Surface) -> None:
    """
    Draws the health bar above the character.
    :param surface: surface to draw the health bar on
    """
    bar_width = Var.DEFAULT_CHARACTER_SIZE[0]
    bar_height = 6
    x = self.__x
    y = self.__y - bar_height - 2
    health_ratio = max(0,
                       self.__health) / self.__max_health if self.__max_health > 0 else 0
    fill_width = int(bar_width * health_ratio)
    pygame.draw.rect(surface, Color.HEALTH_BAR_BG,
                     (x, y, bar_width, bar_height))
    color = Color.HEALTH_BAR_GREEN if health_ratio > 0.3 else Color.HEALTH_BAR_RED
    pygame.draw.rect(surface, color, (x, y, fill_width, bar_height))
    pygame.draw.rect(surface, Color.HEALTH_BAR_BORDER,
                     (x, y, bar_width, bar_height), 1)

  def draw(self, surface: Surface) -> None:
    """
    Draws the zombie and its health bar on the given surface.
    :param surface: surface to draw the character on
    """
    surface.blit(self.__image, (self.__x, self.__y))
    self.draw_health_bar(surface)

  def get_sprites(self) -> dict[str, Surface]:
    """
    Get the character's sprites.
    :return: dictionary of character sprites
    """
    return self.__sprites

  def set_walking_sprites(self, sprites: list[Surface]) -> None:
    """
    Set the walking sprites for the character.
    :param sprites: list of walking sprite surfaces
    """
    self.__walking_sprites = sprites

  def get_step_sounds(self) -> list[SoundType]:
    """
    Get the character's step sounds.
    :return: list of step sound effects
    """
    return self.__step_sounds

  def set_step_sounds(self, sounds: list[SoundType]) -> None:
    """
    Set the step sounds for the character.
    :param sounds:
    """
    self.__step_sounds = sounds

  def set_step_channel(self, channel: pygame.mixer.Channel) -> None:
    """
    Set the audio channel for playing step sounds.
    :param channel: pygame mixer channel
    """
    self.__step_channel = channel


class Hero(Character):
  """Class representing the hero character."""

  def __init__(self, x: int = 0, y: int = 0, health: int = 100) -> None:
    """
    Initializes the hero with default attributes and sprites.
    :param x: initial x position
    :param y: initial y position
    :param health: initial and maximum health
    """
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
        ],
    )
    self.set_walking_sprites([
      self.get_sprites()["walking_1"],
      self.get_sprites()["walking_2"],
      self.get_sprites()["walking_3"],
      self.get_sprites()["walking_4"]
    ])
    self.set_step_sounds([
      SOUNDS.get("pl_step1"),
      SOUNDS.get("pl_step2"),
      SOUNDS.get("pl_step3"),
      SOUNDS.get("pl_step4")
    ])
    self.set_step_channel(pygame.mixer.Channel(5))

  def apply_medkit(self, medkit: 'Medkit') -> None:
    """
    Applies a medkit to heal the hero.
    :param medkit: Medkit object to use
    """
    if not medkit.get_used() and self.get_health() < self.get_max_health():
      heal_amount = medkit.get_heal_amount()
      new_health = min(self.get_health() + heal_amount, self.get_max_health())
      self._set_health(new_health)


class Zombie(Character):
  """Class representing a zombie enemy."""

  def __init__(self, x: int = 0, y: int = 0, health: int = 10) -> None:
    """
    Initializes the zombie with default attributes and sprites.
    :param x: initial x position
    :param y: initial y position
    :param health: initial and maximum health
    """
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
    self.set_walking_sprites([
      self.get_sprites()["walking_1"],
      self.get_sprites()["walking_2"],
      self.get_sprites()["walking_3"]
    ])
    self.set_step_sounds([])
