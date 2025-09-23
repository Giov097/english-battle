"""Global variables"""
from typing import Any

from lib.Color import Color


class Var:
  """Global variables"""
  DEFAULT_CHARACTER_SIZE: tuple[int, int] = (23, 30)
  WALK_FRAME_DELAY_NORMAL: int = 5
  WALK_FRAME_DELAY_BORDER: int = 20
  DAMAGE_DISPLAY_FRAMES: int = 15
  ATTACK_DISPLAY_FRAMES: int = 10

  DEFAULT_WINDOW_SIZE: tuple[int, int] = (640, 480)
  DEFAULT_WALL_THICKNESS: int = 20
  DEFAULT_CELL_SIZE: int = 80
  DEFAULT_DEATH_FADE_DURATION: float = 5.0

  FONT: str = "Roboto"
  TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)

  QUESTIONS = {
    # Fácil
    1: {
      "word_ordering": [
        (("I", "am", "a", "student"), "I am a student"),
        (("She", "is", "happy"), "She is happy"),
        (("They", "are", "playing"), "They are playing"),
        (("We", "have", "a", "dog"), "We have a dog"),
      ],
      "multiple_choice": [
        ("Complete: She ___ happy",
         ["are", "is", "am"], "is"),
        ("Complete: ___ you a student?",
         ["Are", "Is", "Am"],
         "Are"),
        ("Complete: I ___ not a teacher",
         ["not", "am", "are"],
         "am"),
        ("Complete: We ___ a car", ["have", "has", "haves"],
         "have"),
      ],
      "fill_in_the_blank": [
        ("I ___ a student. (to be)", "am"),
        ("She ___ happy. (to be)", "is"),
        ("They ___ playing. (to be)", "are"),
        ("We ___ a dog. (to have)", "have"),
      ]
    },
    # Intermedio bajo
    2: {
      "word_ordering": [
        (("He", "likes", "pizza"), "He likes pizza"),
        (("You", "are", "my", "friend"), "You are my friend"),
        (("The", "cat", "is", "on", "the", "roof"), "The cat is on the roof"),
        (("My", "brother", "is", "tall"), "My brother is tall"),
      ],
      "multiple_choice": [
        ("Choose the correct sentence:",
         ["They is playing", "They are playing", "They are play"],
         "They are playing"),
        ("Which is the correct question?",
         ["Does she likes pizza?", "Does she like pizza?",
          "Do she like pizza?"],
         "Does she like pizza?"),
        ("Select the correct negative:",
         ["You don't are my friend", "You aren't my friend",
          "You not are my friend"], "You aren't my friend"),
        ("Which is correct?",
         ["The cat is on the roof", "The cat are on the roof",
          "The cat is in the roof"], "The cat is on the roof"),
      ],
      "fill_in_the_blank": [
        ("He ___ pizza. (like)", "likes"),
        ("You ___ my friend. (to be)", "are"),
        ("The cat ___ on the roof. (to be)", "is"),
        ("My brother ___ tall. (to be)", "is"),
      ]
    },
    # Intermedio
    3: {
      "word_ordering": [
        (("It", "outside", "is", "raining"), "It is raining outside"),
        (("We", "tomorrow", "are", "going", "to", "the", "park"),
         "We are going to the park tomorrow"),
        (("She", "silver", "has", "a", "car"), "She has a silver car"),
        (("They", "new", "my", "are", "friends"), "They are my new friends"),
      ],
      "multiple_choice": [
        ("Choose the correct sentence:",
         ["It is raining", "It are raining", "It am raining"], "It is raining"),
        ("Which is the correct question?",
         ["Are we going to the park?", "Is we going to the park?",
          "Are we go to the park?"], "Are we going to the park?"),
        ("Select the correct negative:",
         ["She hasn't a car", "She doesn't have a car", "She don't have a car"],
         "She doesn't have a car"),
        ("Which is correct?",
         ["They are friends", "They is friends", "They are friend"],
         "They are friends"),
      ],
      "fill_in_the_blank": [
        ("It ___ raining. (to be)", "is"),
        ("We ___ going to the park. (to be)", "are"),
        ("She ___ a car. (have)", "has"),
        ("They ___ friends (to be)", "are"),
      ]
    },
    # Intermedio alto
    4: {
      "word_ordering": [
        (("I", "listening", "jazz", "love", "music"),
         "I love listening jazz music"),
        (("The", "dog", "mailman", "the", "is", "barking"),
         "The dog is barking the mailman"),
        (("He", "is", "reading", "history", "a", "book"),
         "He is reading a history book"),
        (("You", "have", "a", "nice", "house"), "You have a nice house"),
      ],
      "multiple_choice": [
        ("Choose the correct sentence:",
         ["I love music", "I loves music", "I am love music"], "I love music"),
        ("Which is the correct question?",
         ["Is the dog barking?", "Does the dog barking?", "Is the dog bark?"],
         "Is the dog barking?"),
        ("Select the correct negative:",
         ["He isn't reading a book", "He not is reading a book",
          "He isn't read a book"], "He isn't reading a book"),
        ("Which is correct?",
         ["You have a nice house", "You has a nice house",
          "You have nice house"],
         "You have a nice house"),
      ],
      "fill_in_the_blank": [
        ("I ___ music. (to love)", "love"),
        ("The dog ___ barking. (to be)", "is"),
        ("He is ___ a book. (to read)", "reading"),
        ("You ___ a nice house. (to have)", "have"),
      ]
    },
    # Difícil
    5: {
      "word_ordering": [
        (("left", "I", "dog", "the", "door", "open", "ran out", "and", "the"),
         "I left the door open and the dog ran out"),
        (("The", "children", "are", "playing", "in", "the", "playground"),
         "The children are playing in the playground"),
        (("She", "will", "be", "my", "half", "sister"),
         "She will be my half sister"),
        (("We", "travelled", "to", "Brazil", "last", "year"),
         "We travelled to Brazil last year"),
      ],
      "multiple_choice": [
        ("Choose the correct sentence:",
         ["If I study hard, I'll pass the exam",
          "If I studied hard, I was pass the exam",
          "If I studied hard, I was passing the exam"],
         "If I study hard, I'll pass the exam"),
        ("Which is the correct question?",
         ["Are the children playing?", "Is the children playing?",
          "Are the children play?"], "Are the children playing?"),
        ("Select the correct negative:",
         ["She isn't my sister", "She not is my sister", "She isn't sister my"],
         "She isn't my sister"),
        ("Which is correct?",
         ["It is a beautiful day", "It are a beautiful day",
          "It is beautiful day"], "It is a beautiful day"),
      ],
      "fill_in_the_blank": [
        ("We ___ happy. (to be)", "are"),
        ("The children ___ playing. (to be)", "are"),
        ("She ___ my sister. (to be)", "is"),
        ("It ___ a beautiful day. (to be)", "is"),
      ]
    }
  }

  LEVELS_CONFIG: list[dict[str, Any]] = [
    # Niveles tutoriales
    {
      "name": "Tutorial 1: Movimiento",
      "tutorial": True,
      "tutorial_step": "move",
      "difficulty": 1,
      "type": "multiple_choice",
      "num_zombies": 0,
      "background": "grass",
      "wall_color": Color.WALL_COLOR_GRASS,
      "message": "Usa las flechas de dirección para moverte. Llega hasta la puerta para avanzar."
    },
    {
      "name": "Tutorial 2: Combate",
      "tutorial": True,
      "tutorial_step": "combat",
      "difficulty": 1,
      "type": "multiple_choice",
      "num_zombies": 1,
      "background": "grass",
      "wall_color": Color.WALL_COLOR_GRASS,
      "message": "Acércate al zombi para iniciar un combate. Responde correctamente para atacar."
    },
    {
      "name": "Tutorial 3: Curación",
      "tutorial": True,
      "tutorial_step": "heal",
      "difficulty": 1,
      "type": "multiple_choice",
      "num_zombies": 0,
      "background": "grass",
      "wall_color": Color.WALL_COLOR_GRASS,
      "message": "Parece que nuestro héroe está herido. Recoge el botiquín para curarte. Acércate a él para usarlo."
    },
    {
      "name": "Nivel 1.1 - Multiple Choice",
      "difficulty": 1,
      "type": "multiple_choice",
      "num_zombies": 3,
      "background": "grass",
      "wall_color": Color.WALL_COLOR_GRASS
    },
    {
      "name": "Nivel 1.2 - Word Ordering",
      "difficulty": 1,
      "type": "word_ordering",
      "num_zombies": 3,
      "background": "grass",
      "wall_color": Color.WALL_COLOR_GRASS
    },
    {
      "name": "Nivel 1.3 - Fill in the Blank",
      "difficulty": 1,
      "type": "fill_in_the_blank",
      "num_zombies": 3,
      "background": "grass",
      "wall_color": Color.WALL_COLOR_GRASS
    },
    {
      "name": "Nivel 2.1 - Multiple Choice",
      "difficulty": 2,
      "type": "multiple_choice",
      "num_zombies": 4,
      "background": "cave",
      "wall_color": Color.WALL_COLOR_CAVE
    },
    {
      "name": "Nivel 2.2 - Word Ordering",
      "difficulty": 2,
      "type": "word_ordering",
      "num_zombies": 4,
      "background": "cave",
      "wall_color": Color.WALL_COLOR_CAVE
    },
    {
      "name": "Nivel 2.3 - Fill in the Blank",
      "difficulty": 2,
      "type": "fill_in_the_blank",
      "num_zombies": 4,
      "background": "cave",
      "wall_color": Color.WALL_COLOR_CAVE
    },
    {
      "name": "Nivel 3.1 - Multiple Choice",
      "difficulty": 3,
      "type": "multiple_choice",
      "num_zombies": 5,
      "background": "beach",
      "wall_color": Color.WALL_COLOR_BEACH
    },
    {
      "name": "Nivel 3.2 - Word Ordering",
      "difficulty": 3,
      "type": "word_ordering",
      "num_zombies": 5,
      "background": "beach",
      "wall_color": Color.WALL_COLOR_BEACH
    },
    {
      "name": "Nivel 3.3 - Fill in the Blank",
      "difficulty": 3,
      "type": "fill_in_the_blank",
      "num_zombies": 5,
      "background": "beach",
      "wall_color": Color.WALL_COLOR_BEACH
    },
    {
      "name": "Nivel 4.1 - Multiple Choice",
      "difficulty": 4,
      "type": "multiple_choice",
      "num_zombies": 7,
      "background": "brick-dust",
      "wall_color": Color.WALL_COLOR_BRICKDUST
    },
    {
      "name": "Nivel 4.2 - Word Ordering",
      "difficulty": 4,
      "type": "word_ordering",
      "num_zombies": 7,
      "background": "brick-dust",
      "wall_color": Color.WALL_COLOR_BRICKDUST
    },
    {
      "name": "Nivel 4.3 - Fill in the Blank",
      "difficulty": 4,
      "type": "fill_in_the_blank",
      "num_zombies": 7,
      "background": "brick-dust",
      "wall_color": Color.WALL_COLOR_BRICKDUST
    },
    {
      "name": "Nivel 5.1 - Multiple Choice",
      "difficulty": 5,
      "type": "multiple_choice",
      "num_zombies": 8,
      "background": "moon",
      "wall_color": Color.WALL_COLOR_SNOW
    },
    {
      "name": "Nivel 5.2 - Word Ordering",
      "difficulty": 5,
      "type": "word_ordering",
      "num_zombies": 8,
      "background": "moon",
      "wall_color": Color.WALL_COLOR_SNOW
    },
    {
      "name": "Nivel 5.3 - Fill in the Blank",
      "difficulty": 5,
      "type": "fill_in_the_blank",
      "num_zombies": 8,
      "background": "moon",
      "wall_color": Color.WALL_COLOR_SNOW
    }
  ]
