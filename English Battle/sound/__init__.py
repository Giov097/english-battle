"""Module to load and manage sound effects for the game."""

import pygame
import os

from pygame.mixer import SoundType

pygame.mixer.init()
SOUND_DIR = os.path.dirname(__file__)

SOUNDS: dict[str, SoundType] = {}

MUSIC: dict[str, str] = {}

for filename in os.listdir(os.path.join(SOUND_DIR, 'sfx')):
  if filename.lower().endswith(('.wav', '.ogg', '.mp3')):
    sound_name = os.path.splitext(filename)[0]
    SOUNDS[sound_name] = pygame.mixer.Sound(
      os.path.join(SOUND_DIR, 'sfx', filename))

for filename in os.listdir(os.path.join(SOUND_DIR, 'music')):
  if filename.lower().endswith(('.mp3', '.ogg', '.wav')):
    music_name = os.path.splitext(filename)[0]
    MUSIC[music_name] = os.path.join(SOUND_DIR, 'music', filename)
