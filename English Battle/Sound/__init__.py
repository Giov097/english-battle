import pygame
import os

pygame.mixer.init()
SOUND_DIR = os.path.dirname(__file__)

SOUNDS = {}

for filename in os.listdir(SOUND_DIR):
  if filename.lower().endswith(('.wav', '.ogg', '.mp3')):
    sound_name = os.path.splitext(filename)[0]
    SOUNDS[sound_name] = pygame.mixer.Sound(os.path.join(SOUND_DIR, filename))
