"""Functions"""
from lib.Color import Color
from lib.Level import (Level, TutorialLevel, TutorialCombatLevel,
                       TutorialMoveLevel, TutorialHealLevel, LevelType)
from lib.Var import Var


def create_level_from_config(config: dict, hero: 'Hero') -> Level:
  """Creates a Level or TutorialLevel based on the config dictionary."""
  if config.get("tutorial"):
    step = config.get("tutorial_step")
    if step == "move":
      return TutorialMoveLevel(config, hero)
    elif step == "combat":
      return TutorialCombatLevel(config,hero)
    elif step == "heal":
      return TutorialHealLevel(config,hero)
    else:
      return TutorialLevel(config,hero)
  else:
    return Level(
        background_name=config.get("background", "grass"),
        difficulty=config.get("difficulty", 1),
        level_type=LevelType[config.get("type").upper()],
        window_size=Var.DEFAULT_WINDOW_SIZE,
        wall_color=config.get("wall_color", Color.WALL_COLOR_GRASS)
    )
