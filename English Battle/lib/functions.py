"""Functions"""
from lib.color import Color
from lib.level import (Level, TutorialLevel, TutorialCombatLevel,
                       TutorialMoveLevel, TutorialHealLevel, LevelType)
from lib.var import Var


def create_level_from_config(config: dict, hero: 'Hero') -> Level:
  """
  Creates a Level or TutorialLevel based on the config dictionary.
  :param config: Configuration dictionary for the level.
  :param hero: The hero character for the level.
  :return: An instance of Level or TutorialLevel.
  """
  level: Level
  if config.get("tutorial"):
    step = config.get("tutorial_step")
    if step == "move":
      level = TutorialMoveLevel(config, hero)
    elif step == "combat":
      level = TutorialCombatLevel(config, hero)
    elif step == "heal":
      level = TutorialHealLevel(config, hero)
    else:
      level = TutorialLevel(config, hero)
  else:
    level = Level(
        background_name=config.get("background", "grass"),
        difficulty=config.get("difficulty", 1),
        level_type=LevelType[config.get("type").upper()],
        window_size=Var.DEFAULT_WINDOW_SIZE,
        wall_color=config.get("wall_color", Color.WALL_COLOR_GRASS),
        hero=hero)
  return level
