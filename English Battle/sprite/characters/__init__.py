"""
This module loads and provides access to the hero character sprites.
"""
import pygame
import os

SPRITE_DIR = os.path.dirname(__file__)

HERO_SPRITES = {
  "base": pygame.image.load(os.path.join(SPRITE_DIR, "hero", "base.png")),
  "damage": pygame.image.load(os.path.join(SPRITE_DIR, "hero", "damage.png")),
  "dead": pygame.image.load(os.path.join(SPRITE_DIR, "hero", "dead.png")),
  "attack": pygame.image.load(os.path.join(SPRITE_DIR, "hero", "attack.png")),
  "ducking": pygame.image.load(os.path.join(SPRITE_DIR, "hero", "ducking.png")),
  "jumping": pygame.image.load(os.path.join(SPRITE_DIR, "hero", "jumping.png")),
  "walking_1": pygame.image.load(
      os.path.join(SPRITE_DIR, "hero", "walking-1.png")),
  "walking_2": pygame.image.load(
      os.path.join(SPRITE_DIR, "hero", "walking-2.png")),
  "walking_3": pygame.image.load(
      os.path.join(SPRITE_DIR, "hero", "walking-3.png")),
  "walking_4": pygame.image.load(
      os.path.join(SPRITE_DIR, "hero", "walking-4.png")),
}
