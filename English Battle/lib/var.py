"""Global variables"""
from typing import Any

import pygame

from lib.color import Color


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

  TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)

  QUESTIONS = {
    # Fácil
    1: {
      "word_ordering": [
        (("I", "am", "a", "student"), "I am a student"),
        (("She", "is", "happy"), "She is happy"),
        (("They", "are", "playing"), "They are playing"),
        (("We", "have", "a", "dog"), "We have a dog"),
        (("He", "is", "my", "friend"), "He is my friend"),
        (("You", "are", "tired"), "You are tired"),
        (("It", "is", "cold", "today"), "It is cold today"),
        (("We", "are", "in", "the", "park"), "We are in the park"),
        (("The", "book", "is", "on", "the", "table"),
         "The book is on the table"),
        (("She", "has", "a", "red", "car"), "She has a red car"),
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
        ("Complete: He ___ my friend",
         ["is", "are", "am"], "is"),
        ("Complete: ___ it cold today?",
         ["Is", "Are", "Am"], "Is"),
        ("Complete: You ___ tired",
         ["is", "are", "am"], "are"),
        ("Complete: We ___ in the park",
         ["is", "are", "am"], "are"),
        ("Complete: The book ___ on the table",
         ["is", "are", "am"], "is"),
        ("Complete: She ___ a red car",
         ["has", "have", "had"], "has"),
      ],
      "fill_in_the_blank": [
        ("I ___ a student. (to be)", "am"),
        ("She ___ happy. (to be)", "is"),
        ("They ___ playing. (to be)", "are"),
        ("We ___ a dog. (to have)", "have"),
        ("He ___ my friend. (to be)", "is"),
        ("It ___ cold today. (to be)", "is"),
        ("You ___ tired. (to be)", "are"),
        ("We ___ in the park. (to be)", "are"),
        ("The book ___ on the table. (to be)", "is"),
        ("She ___ a red car. (have)", "has"),
      ],
      "speed_level": "lento"
    },
    # Intermedio bajo
    2: {
      "word_ordering": [
        (("He", "is", "eating", "pizza"), "He is eating pizza"),
        (("You", "are", "not", "my", "friend"), "You are not my friend"),
        (("The", "cat", "is", "not", "on", "the", "roof"),
         "The cat is not on the roof"),
        (("My", "brother", "is", "playing", "football"),
         "My brother is playing football"),
        (("Are", "you", "studying", "English"), "Are you studying English?"),
        (("We", "are", "watching", "a", "movie"), "We are watching a movie"),
        (("She", "is", "not", "here"), "She is not here"),
      ],
      "multiple_choice": [
        ("Choose the correct negative:",
         ["He not eating pizza", "He isn't eating pizza",
          "He doesn't eating pizza"],
         "He isn't eating pizza"),
        ("Which is the correct question?",
         ["Is the cat on the roof?", "Does the cat on the roof?",
          "Are the cat on the roof?"],
         "Is the cat on the roof?"),
        ("Select the correct present continuous:",
         ["My brother is play football", "My brother is playing football",
          "My brother playing football"],
         "My brother is playing football"),
        ("Which is correct?",
         ["You are not my friend", "You not are my friend",
          "You aren't my friend"],
         "You aren't my friend"),
        ("Choose the correct answer:",
         ["Are you studying English?", "Do you studying English?",
          "Is you studying English?"],
         "Are you studying English?"),
        ("Select the correct negative:",
         ["She is not here", "She not is here", "She are not here"],
         "She is not here"),
        ("Choose the correct sentence:",
         ["We are watching a movie", "We watching are a movie",
          "We are movie watching"],
         "We are watching a movie"),
      ],
      "fill_in_the_blank": [
        ("He ___ eating pizza. (to be)", "is"),
        ("You ___ not my friend. (to be)", "are"),
        ("The cat ___ not on the roof. (to be)", "is"),
        ("My brother is ___ football. (to play)", "playing"),
        ("___ you studying English? (to be)", "Are"),
        ("We ___ watching a movie. (to be)", "are"),
        ("She ___ not here. (to be)", "is"),
      ],
      "speed_level": "normal"
    },
    # Intermedio
    3: {
      "word_ordering": [
        (("It", "outside", "is", "raining"), "It is raining outside"),
        (("We", "tomorrow", "are", "going", "to", "the", "park"),
         "We are going to the park tomorrow"),
        (("She", "silver", "has", "a", "car"), "She has a silver car"),
        (("They", "new", "my", "are", "friends"), "They are my new friends"),
        (("Yesterday", "was", "cold", "very"), "Yesterday was very cold"),
        (("He", "was", "reading", "a", "book", "last", "night"),
         "He was reading a book last night"),
        (("We", "played", "football", "in", "the", "park"),
         "We played football in the park"),
        (("They", "were", "studying", "for", "the", "exam"),
         "They were studying for the exam"),
        (("I", "have", "never", "been", "to", "London"),
         "I have never been to London"),
        (("She", "was", "not", "feeling", "well"), "She was not feeling well"),
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
        ("Choose the correct past simple sentence:",
         ["We play football yesterday", "We played football yesterday",
          "We playing football yesterday"], "We played football yesterday"),
        ("Select the correct past continuous:",
         ["He was reading a book", "He were reading a book",
          "He was read a book"], "He was reading a book"),
        ("Which is the correct negative in past:",
         ["They didn't studied for the exam", "They didn't study for the exam",
          "They don't study for the exam"], "They didn't study for the exam"),
        ("Choose the correct question in past:",
         ["Did you went to the party?", "Did you go to the party?",
          "Do you go to the party?"], "Did you go to the party?"),
        ("Select the correct present perfect:",
         ["I have never been to London", "I never have been to London",
          "I have never be to London"],
         "I have never been to London"),
        ("Choose the correct negative sentence:",
         ["She was not feeling well", "She not was feeling well",
          "She was feeling not well"],
         "She was not feeling well"),
      ],
      "fill_in_the_blank": [
        ("It ___ raining. (to be)", "is"),
        ("We ___ going to the park. (to be)", "are"),
        ("She ___ a car. (have)", "has"),
        ("They ___ friends (to be)", "are"),
        ("Yesterday ___ very cold. (to be)", "was"),
        ("He ___ reading a book last night. (to be)", "was"),
        ("We ___ football in the park. (play, past)", "played"),
        ("They ___ studying for the exam. (to be, past)", "were"),
        ("I ___ not go to the party. (do, past)", "did"),
        ("Did you ___ your homework? (do, past)", "do"),
        ("I ___ never been to London. (have)", "have"),
        ("She ___ not feeling well. (to be, past)", "was"),
      ],
      "speed_level": "rápido"
    },
    # Intermedio alto
    4: {
      "word_ordering": [
        (("I", "have", "been", "listening", "to", "jazz", "music"),
         "I have been listening to jazz music"),
        (("The", "dog", "was", "barking", "at", "the", "mailman"),
         "The dog was barking at the mailman"),
        (("He", "will", "be", "reading", "a", "history", "book"),
         "He will be reading a history book"),
        (("You", "had", "bought", "a", "nice", "house"),
         "You had bought a nice house"),
        (("She", "has", "never", "visited", "London"),
         "She has never visited London"),
        (("If", "it", "rains", "we", "will", "stay", "home"),
         "If it rains, we will stay home"),
        (("They", "should", "have", "finished", "the", "project"),
         "They should have finished the project"),
        (("We", "have", "been", "waiting", "for", "hours"),
         "We have been waiting for hours"),
        (("He", "had", "already", "left", "when", "I", "arrived"),
         "He had already left when I arrived"),
      ],
      "multiple_choice": [
        ("Choose the correct sentence:",
         ["I have been listening to music", "I has been listening to music",
          "I am been listening to music", "I listened music"],
         "I have been listening to music"),
        ("Which is the correct question?",
         ["Was the dog barking at the mailman?",
          "Did the dog barking at the mailman?",
          "Is the dog barked at the mailman?",
          "Is the dog barking at the mailman?"],
         "Was the dog barking at the mailman?"),
        ("Select the correct negative:",
         ["He won't be reading a book", "He not will be reading a book",
          "He doesn't will be reading a book", "He won't reading a book"],
         "He won't be reading a book"),
        ("Which is correct?",
         ["You had bought a nice house", "You have bought a nice house",
          "You has bought a nice house", "You had buy a nice house"],
         "You had bought a nice house"),
        ("Choose the correct present perfect sentence:",
         ["She has never visit London", "She never has visited London",
          "She has never visited London", "She have never visited London"],
         "She has never visited London"),
        ("Select the correct conditional:",
         ["If it rains, we will stay home", "If it rain, we will stay home",
          "If it rains, we stays home", "If it raining, we will stay home"],
         "If it rains, we will stay home"),
        ("Choose the correct modal perfect:",
         ["They should have finished the project",
          "They should has finished the project",
          "They should finished the project",
          "They should have finish the project"],
         "They should have finished the project"),
        ("Select the correct present perfect continuous:",
         ["We have been waiting for hours", "We has been waiting for hours",
          "We have waiting for hours"],
         "We have been waiting for hours"),
        ("Choose the correct past perfect:",
         ["He had already left when I arrived",
          "He has already left when I arrived",
          "He had left already when I arrived"],
         "He had already left when I arrived"),
      ],
      "fill_in_the_blank": [
        ("I ___ been listening to music. (have)", "have"),
        ("The dog ___ barking at the mailman. (to be, past)", "was"),
        ("He ___ be reading a book. (will)", "will"),
        ("You ___ bought a nice house. (had)", "had"),
        ("She ___ never visited London. (has)", "has"),
        ("If it ___, we will stay home. (to rain)", "rains"),
        ("They should ___ finished the project. (have)", "have"),
        ("We ___ been waiting for hours. (have)", "have"),
        ("He ___ already left when I arrived. (had)", "had"),
      ],
      "speed_level": "muy rápido"
    },
    # Difícil
    5: {
      "word_ordering": [
        (("If", "I", "had", "known", "about", "the", "party", "I", "would",
          "have", "gone"), "If I had known about the party, I would have gone"),
        (("The", "children", "had", "been", "playing", "in", "the",
          "playground", "before", "it", "started", "to", "rain"),
         "The children had been playing in the playground before it started to rain"),
        (("She", "will", "have", "become", "my", "half", "sister", "by", "next",
          "year"), "She will have become my half sister by next year"),
        (("We", "were", "travelling", "to", "Brazil", "when", "the", "storm",
          "hit"), "We were travelling to Brazil when the storm hit"),
        (("Had", "he", "been", "working", "all", "night"),
         "Had he been working all night?"),
        (("If", "they", "had", "arrived", "earlier", "they", "would", "have",
          "seen", "the", "show"),
         "If they had arrived earlier, they would have seen the show"),
      ],
      "multiple_choice": [
        ("Choose the correct sentence:",
         ["If I had studied harder, I would have passed the exam",
          "If I studied harder, I will have passed the exam",
          "If I study harder, I would have passed the exam"],
         "If I had studied harder, I would have passed the exam"),
        ("Which is the correct question?",
         ["Had the children been playing before it rained?",
          "Did the children been playing before it rained?",
          "Were the children been playing before it rained?"],
         "Had the children been playing before it rained?"),
        ("Select the correct negative:",
         ["She will not have become my sister",
          "She will have not become my sister",
          "She not will have become my sister"],
         "She will not have become my sister"),
        ("Which is correct?",
         ["We were travelling when the storm hit",
          "We was travelling when the storm hit",
          "We were travel when the storm hit"],
         "We were travelling when the storm hit"),
        ("Choose the correct past perfect continuous question:",
         ["Had he been working all night?", "Has he been working all night?",
          "Had he working all night?"],
         "Had he been working all night?"),
        ("Select the correct conditional perfect:",
         ["If they had arrived earlier, they would have seen the show",
          "If they arrived earlier, they would have seen the show",
          "If they had arrived earlier, they would see the show"],
         "If they had arrived earlier, they would have seen the show"),
      ],
      "fill_in_the_blank": [
        ("If I ___ known, I would have gone. (have, past perfect)", "had"),
        ("The children ___ been playing before it rained. (have, past perfect continuous)",
         "had"),
        ("She will ___ become my sister by next year. (have, future perfect)",
         "have"),
        ("We ___ travelling when the storm hit. (to be, past continuous)",
         "were"),
        ("Had he ___ working all night? (been)", "been"),
        ("If they ___ arrived earlier, they would have seen the show. (had)",
         "had"),
      ],
      "speed_level": "extremo"
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

  MUSIC_CHANNEL = pygame.mixer.music
  SFX_CHANNEL = pygame.mixer.Channel(7)
