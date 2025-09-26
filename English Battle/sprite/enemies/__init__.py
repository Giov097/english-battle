"""sprite assets for enemies."""

import pygame
import os

SPRITE_DIR = os.path.dirname(__file__)

ZOMBIE_SPRITES = {
  "base": pygame.image.load(os.path.join(SPRITE_DIR, "zombie", "base.png")),
  "attack": pygame.image.load(os.path.join(SPRITE_DIR, "zombie", "attack.png")),
  "damage": pygame.image.load(os.path.join(SPRITE_DIR, "zombie", "damage.png")),
  "dead": pygame.image.load(os.path.join(SPRITE_DIR, "zombie", "dead-2.png")),
  "walking_1": pygame.image.load(
      os.path.join(SPRITE_DIR, "zombie", "walking-1.png")),
  "walking_2": pygame.image.load(
      os.path.join(SPRITE_DIR, "zombie", "walking-2.png")),
  "walking_3": pygame.image.load(
      os.path.join(SPRITE_DIR, "zombie", "walking-3.png")),
}
