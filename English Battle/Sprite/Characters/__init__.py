import pygame
import os

SPRITE_DIR = os.path.dirname(__file__)

HERO_SPRITES = {
  "base": pygame.image.load(os.path.join(SPRITE_DIR, "Hero", "base.png")),
  "damage": pygame.image.load(os.path.join(SPRITE_DIR, "Hero", "damage.png")),
  "dead": pygame.image.load(os.path.join(SPRITE_DIR, "Hero", "dead.png")),
  "attack": pygame.image.load(os.path.join(SPRITE_DIR, "Hero", "attack.png")),
  "ducking": pygame.image.load(os.path.join(SPRITE_DIR, "Hero", "ducking.png")),
  "jumping": pygame.image.load(os.path.join(SPRITE_DIR, "Hero", "jumping.png")),
  "walking_1": pygame.image.load(
      os.path.join(SPRITE_DIR, "Hero", "walking-1.png")),
  "walking_2": pygame.image.load(
      os.path.join(SPRITE_DIR, "Hero", "walking-2.png")),
  "walking_3": pygame.image.load(
      os.path.join(SPRITE_DIR, "Hero", "walking-3.png")),
  "walking_4": pygame.image.load(
      os.path.join(SPRITE_DIR, "Hero", "walking-4.png")),
}
