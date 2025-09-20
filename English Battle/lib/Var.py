"""Global variables"""

DEFAULT_CHARACTER_SIZE = (23, 30)
WALK_FRAME_DELAY_NORMAL = 5
WALK_FRAME_DELAY_BORDER = 20
DAMAGE_DISPLAY_FRAMES = 15
ATTACK_DISPLAY_FRAMES = 10

DEFAULT_WINDOW_SIZE = (640, 480)
DEFAULT_WALL_THICKNESS = 20
DEFAULT_CELL_SIZE = 80
DEFAULT_DEATH_FADE_DURATION = 5.0

# Preguntas por dificultad y tipo de nivel
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
      ("Complete: We ___ a car", ["have", "ha", "haves"],
       "have"),
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
       ["Does she likes pizza?", "Does she like pizza?", "Do she like pizza?"],
       "Does she like pizza?"),
      ("Select the correct negative:",
       ["You don't are my friend", "You aren't my friend",
        "You not are my friend"], "You aren't my friend"),
      ("Which is correct?",
       ["The cat is on the roof", "The cat are on the roof",
        "The cat is in the roof"], "The cat is on the roof"),
    ]
  },
  # Intermedio
  3: {
    "word_ordering": [
      (("It", "is", "raining"), "It is raining"),
      (("We", "are", "going", "to", "the", "park"), "We are going to the park"),
      (("She", "has", "a", "car"), "She has a car"),
      (("They", "are", "friends"), "They are friends"),
    ],
    "multiple_choice": [
      ("Choose the correct sentence:",
       ["It is raining", "It are raining", "It raining"], "It is raining"),
      ("Which is the correct question?",
       ["Are we going to the park?", "Is we going to the park?",
        "Are we go to the park?"], "Are we going to the park?"),
      ("Select the correct negative:",
       ["She hasn't a car", "She doesn't have a car", "She don't have a car"],
       "She doesn't have a car"),
      ("Which is correct?",
       ["They are friends", "They is friends", "They are friend"],
       "They are friends"),
    ]
  },
  # Intermedio alto
  4: {
    "word_ordering": [
      (("I", "love", "music"), "I love music"),
      (("The", "dog", "is", "barking"), "The dog is barking"),
      (("He", "is", "reading", "a", "book"), "He is reading a book"),
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
       ["You have a nice house", "You has a nice house", "You have nice house"],
       "You have a nice house"),
    ]
  },
  # Difícil
  5: {
    "word_ordering": [
      (("We", "are", "happy"), "We are happy"),
      (("The", "children", "are", "playing"), "The children are playing"),
      (("She", "is", "my", "sister"), "She is my sister"),
      (("It", "is", "a", "beautiful", "day"), "It is a beautiful day"),
    ],
    "multiple_choice": [
      ("Choose the correct sentence:",
       ["We are happy", "We is happy", "We happy"], "We are happy"),
      ("Which is the correct question?",
       ["Are the children playing?", "Is the children playing?",
        "Are the children play?"], "Are the children playing?"),
      ("Select the correct negative:",
       ["She isn't my sister", "She not is my sister", "She isn't sister my"],
       "She isn't my sister"),
      ("Which is correct?", ["It is a beautiful day", "It are a beautiful day",
                             "It is beautiful day"], "It is a beautiful day"),
    ]
  }
}
