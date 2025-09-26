"""
font resources for the game.
"""
import os

FONTS_DIR = os.path.dirname(__file__)

FONTS: dict[str, str] = {
  "press-start-2p": os.path.join(FONTS_DIR, "PressStart2P.ttf"),
  "retro-british": os.path.join(FONTS_DIR, "RetroBritish.otf"),
  "roboto": os.path.join(FONTS_DIR, "Roboto.ttf")
}
