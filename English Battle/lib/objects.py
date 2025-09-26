"""Module for game objects like doors and medkits."""
import random

import pygame

from lib.var import Var
from sound import SOUNDS


class Door:
  """Class representing a door in the level."""

  def __init__(self, x: int, y: int,
      sprite_dict: dict[str, 'Surface']) -> None:
    """
    Initializes the door object.
    :param x: The x-coordinate of the door.
    :param y: The y-coordinate of the door.
    :param sprite_dict: A dictionary of sprites for different door states.
    """
    self.__x = x
    self.__y = y
    self.__sprites = sprite_dict
    self.__state = "closed"
    self.__opening_frame = 0
    self.__image = self.__sprites["closed"]
    self.__open_sounds = [SOUNDS.get("doormove9"), SOUNDS.get("doormove10")]

  def get_x(self) -> int:
    """
    Returns the x-coordinate of the door.
    :return The x-coordinate of the door.
    """
    return self.__x

  def get_y(self) -> int:
    """
    Returns the y-coordinate of the door.
    :return The y-coordinate of the door.
    """
    return self.__y

  def get_state(self) -> str:
    """
    Returns the current state of the door.
    :return The current state of the door.
    """
    return self.__state

  def open(self) -> None:
    """
    Starts the opening animation.
    """
    if self.__state == "closed":
      if self.__open_sounds:
        channel = Var.SFX_CHANNEL
        if channel:
          channel.play(random.choice(self.__open_sounds))
      self.__state = "opening"
      self.__opening_frame = 0

  def animate_opening(self) -> None:
    """
    Animates the door opening using available sprites.
    """
    if self.__state == "opening":
      frames = [
        self.__sprites.get("opening-1"),
        self.__sprites.get("opening-2"),
        self.__sprites.get("opening-3"),
        self.__sprites.get("open")
      ]
      if self.__opening_frame < len(frames):
        self.__image = frames[self.__opening_frame]
        self.__opening_frame += 1
      else:
        self.__image = self.__sprites["open"]
        self.__state = "open"

  def draw(self, surface: 'Surface') -> None:
    """
    Draws the door on the given surface.
    :param surface: The surface to draw the door on.
    """
    surface.blit(self.__image, (self.__x, self.__y))


class Medkit:
  """Class representing a medkit in the level."""

  def __init__(self, x: int, y: int,
      sprite_dict: dict[str, 'Surface']) -> None:
    """
    Initializes the medkit object.
    :param x: The x-coordinate of the medkit.
    :param y: The y-coordinate of the medkit.
    :param sprite_dict: A dictionary of sprites for the medkit.
    """
    self.__x = x
    self.__y = y
    self.__sprites = sprite_dict
    self.__image = self.__sprites["base"]
    self.__used = False
    self.__sounds = [SOUNDS.get("smallmedkit1"), SOUNDS.get("smallmedkit2")]
    self.__heal_amount = 25

  def get_x(self) -> int:
    """
    Returns the x-coordinate of the medkit.
    :return The x-coordinate of the medkit.
    """
    return self.__x

  def get_y(self) -> int:
    """
    Returns the y-coordinate of the medkit.
    :return The y-coordinate of the medkit.
    """
    return self.__y

  def draw(self, surface: 'Surface') -> None:
    """
    Draws the medkit on the given surface.
    :param surface: The surface to draw the medkit on.
    """
    if not self.__used:
      surface.blit(self.__image, (self.__x, self.__y))

  def apply(self, hero: 'Hero') -> None:
    """
    Heals the hero and plays a sound.
    :param hero: The hero to heal.
    """
    if not self.__used and hero.get_health() < hero.get_max_health():
      hero.apply_medkit(self)
      self.__used = True
      sound = random.choice(self.__sounds)
      if sound:
        sound.play()

  def get_used(self) -> bool:
    """
    Returns whether the medkit has been used.
    :return True if the medkit has been used, False otherwise.
    """
    return self.__used

  def get_heal_amount(self) -> int:
    """
    Returns the amount of health the medkit restores.
    :return The amount of health the medkit restores.
    """
    return self.__heal_amount
