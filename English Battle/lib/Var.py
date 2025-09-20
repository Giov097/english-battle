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
    ]
  },
  # Intermedio bajo
  2: {
    "word_ordering": [
      (("He", "likes", "pizza"), "He likes pizza"),
      (("You", "are", "my", "friend"), "You are my friend"),
      (("The", "cat", "is", "on", "the", "roof"), "The cat is on the roof"),
      (("My", "brother", "is", "tall"), "My brother is tall"),
    ]
  },
  # Intermedio
  3: {
    "word_ordering": [
      (("It", "is", "raining"), "It is raining"),
      (("We", "are", "going", "to", "the", "park"), "We are going to the park"),
      (("She", "has", "a", "car"), "She has a car"),
      (("They", "are", "friends"), "They are friends"),
    ]
  },
  # Intermedio alto
  4: {
    "word_ordering": [
      (("I", "love", "music"), "I love music"),
      (("The", "dog", "is", "barking"), "The dog is barking"),
      (("He", "is", "reading", "a", "book"), "He is reading a book"),
      (("You", "have", "a", "nice", "house"), "You have a nice house"),
    ]
  },
  # Difícil
  5: {
    "word_ordering": [
      (("We", "are", "happy"), "We are happy"),
      (("The", "children", "are", "playing"), "The children are playing"),
      (("She", "is", "my", "sister"), "She is my sister"),
      (("It", "is", "a", "beautiful", "day"), "It is a beautiful day"),
    ]
  }
}
