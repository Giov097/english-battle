import pygame
import os

BACKGROUND_DIR = os.path.dirname(__file__)

BACKGROUNDS = {
  "beach": pygame.image.load(os.path.join(BACKGROUND_DIR, "beach.png")),
  "brick-dust": pygame.image.load(os.path.join(BACKGROUND_DIR, "brick-dust.png")),
  "cave": pygame.image.load(os.path.join(BACKGROUND_DIR, "cave.png")),
  "concrete": pygame.image.load(os.path.join(BACKGROUND_DIR, "concrete.png")),
  "dirt": pygame.image.load(os.path.join(BACKGROUND_DIR, "dirt.png")),
  "grass": pygame.image.load(os.path.join(BACKGROUND_DIR, "grass.png")),
  "moon": pygame.image.load(os.path.join(BACKGROUND_DIR, "moon.png")),
  "sand": pygame.image.load(os.path.join(BACKGROUND_DIR, "sand.png")),
  "snow": pygame.image.load(os.path.join(BACKGROUND_DIR, "snow.png")),
}
