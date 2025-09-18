"""Sprite assets for enemies."""

import pygame
import os

SPRITE_DIR = os.path.dirname(__file__)

ZOMBIE_SPRITES = {
  "base": pygame.image.load(os.path.join(SPRITE_DIR, "Zombie", "base.png")),
  "damage": pygame.image.load(os.path.join(SPRITE_DIR, "Zombie", "damage.png")),
  "dead": pygame.image.load(os.path.join(SPRITE_DIR, "Zombie", "dead-2.png")),
  "walking_1": pygame.image.load(
      os.path.join(SPRITE_DIR, "Zombie", "walking-1.png")),
  "walking_2": pygame.image.load(
      os.path.join(SPRITE_DIR, "Zombie", "walking-2.png")),
  "walking_3": pygame.image.load(
      os.path.join(SPRITE_DIR, "Zombie", "walking-3.png")),
}
