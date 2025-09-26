"""sprite assets for levels"""

import pygame
import os

SPRITE_DIR = os.path.dirname(__file__)

DOOR_1_SPRITES = {
  "closed": pygame.image.load(
      os.path.join(SPRITE_DIR, "door", "door1-closed.png")),
  "open": pygame.image.load(os.path.join(SPRITE_DIR, "door", "door-open.png")),
  "opening-1": pygame.image.load(
      os.path.join(SPRITE_DIR, "door", "door1-opening-1.png")),
  "opening-2": pygame.image.load(
      os.path.join(SPRITE_DIR, "door", "door1-opening-2.png")),
  "opening-3": pygame.image.load(
      os.path.join(SPRITE_DIR, "door", "door1-opening-3.png"))
}

MEDKIT_SPRITES = {
  "base": pygame.image.load(
      os.path.join(SPRITE_DIR, "medkit", "medkit.png")),
}
