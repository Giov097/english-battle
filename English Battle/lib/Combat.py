"""
Module to manage combat encounters with grammar questions in a Pygame application.
"""
import random
from abc import ABC, abstractmethod
from typing import Optional, Any

import pygame
from pygame import Rect, Surface, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.event import EventType
from pygame.font import FontType, Font

from lib.Color import Color


class Combat:
  """Class to manage combat encounters with grammar questions."""

  def __init__(self, hero: 'Hero', enemy: 'Character', current_type: str,
      questions_set: list[dict[str, list[str]]]) -> None:
    """
    Initializes the Combat instance.
    :param hero: The hero character.
    :param enemy: The enemy character.
    :param current_type: The type of combat (e.g., "word_ordering", "multiple_choice", "fill_in_the_blank").
    :param questions_set: List of questions for the combat.
    """
    self.__hero: 'Hero' = hero
    self.__enemy: 'Character' = enemy
    self.__combat_type: str = current_type
    self.__active: bool = True
    self.__current_question: str | tuple[str, list[str], str] | None = None
    self.__current_answer: str | None = None
    self.__last_question: str | None = None
    self.__questions_set = questions_set if questions_set is not None else []

  def generate_question(self) -> tuple[str | None, list[
    dict[str, list[str]]] | None, str | None] | str | None:
    """
    Generates a new grammar question (word ordering or multiple choice).
    :return: The generated question and its answer.
    """
    if not self.__questions_set:
      self.__current_question = None
      self.__current_answer = None
    if self.__combat_type == "word_ordering":
      response = self.__generate_word_order_question(self.__questions_set)
    elif self.__combat_type == "multiple_choice":
      response = self.__generate_multiple_choice_question(self.__questions_set)
    elif self.__combat_type == "fill_in_the_blank":
      response = self.__generate_fill_blank_question(self.__questions_set)
    else:
      response = ""
    return response

  def __generate_fill_blank_question(self,
      questions: list[dict[str, list[str]]]) -> str | None:
    """
    Generates a fill-in-the-blank question.
    :param questions: set of questions to choose from.
    :return: The generated question string.
    """
    question: Optional[str] = None
    answer: Optional[str] = None
    same_question = True
    while same_question:
      question, answer = random.choice(questions)
      if question != self.__last_question:
        same_question = False
    self.__current_question = question
    self.__current_answer = answer
    self.__last_question = question
    return self.__current_question

  def __generate_multiple_choice_question(self,
      questions: list[dict[str, list[str]]]) -> tuple[
    str | None, list[dict[str, list[str]]] | None, str | None]:
    """
    Generates a multiple choice question.
    :param questions:  List of questions to choose from.
    :return:  The generated question, options, and answer.
    """
    question: Optional[str] = None
    answer: Optional[str] = None
    options: Optional[list[dict[str, list[str]]]] = None
    same_question = True
    while same_question:
      question, options, answer = random.choice(questions)
      if question != self.__last_question:
        same_question = False
    self.__current_question = (question, options, answer)
    self.__current_answer = answer
    self.__last_question = question
    return self.__current_question

  def __generate_word_order_question(self, questions: list) -> str | None:
    """
    Generates a word ordering question.
    :param questions: List of questions to choose from.
    :return:  The generated question string.
    """
    question: Optional[str] = None
    answer: Optional[str] = None
    same_question = True
    while same_question:
      words, answer = random.choice(questions)
      shuffled_words = list(words)
      random.shuffle(shuffled_words)
      question = " / ".join(shuffled_words)
      if question != self.__last_question:
        same_question = False
    self.__current_question = question
    self.__current_answer = answer
    self.__last_question = question
    return self.__current_question

  def check_answer(self, player_answer: str) -> bool:
    """
    Checks if the player's answer is correct.
    :param player_answer: The answer provided by the player.
    :return: True if the answer is correct, False otherwise.
    """
    return player_answer.strip().lower() == self.__current_answer.strip().lower()

  def process_turn(self, player_answer: str) -> str:
    """
    Processes the turn based on player's answer. If both survive, generates a new question.
    :param player_answer: The answer provided by the player.
    :return: Result message indicating the outcome of the turn.
    """
    if not self.__active or not self.__hero.is_alive() or not self.__enemy.is_alive():
      # TODO: manejar
      pass
    if self.check_answer(player_answer):
      self.__hero.attack(self.__enemy)
      result = "¡Correcto! Atacas al enemigo."
    else:
      self.__enemy.attack(self.__hero)
      result = "Incorrecto. El enemigo te ataca."
    if not self.__enemy.is_alive() or not self.__hero.is_alive():
      self.__active = False
    else:
      self.generate_question()
    return result

  def get_current_question(self) -> str | tuple[str, list[str], str] | None:
    """
    Returns the current question.
    :return: The current question.
    """
    return self.__current_question

  def get_active(self) -> bool:
    """
    Returns whether the combat is still active.
    :return: True if combat is active, False otherwise.
    """
    return self.__active

  def get_combat_type(self) -> str:
    """
    Returns the combat type.
    :return: The combat type.
    """
    return self.__combat_type


def _render_text_multiline(text: str, font_path, base_size: int,
    max_width: int,
    color: tuple[int, int, int]) -> list[Any]:
  """
  Renders text into multiple lines to fit within max_width, adjusting font size if necessary.
  :param text: The text to render.
  :param font_path: Path to the font file.
  :param base_size: The base font size to start with.
  :param max_width: The maximum width for each line.
  :param color: The color of the text.
  :return: List of rendered text surfaces.
  """
  words = text.split(' ')
  font_size = base_size
  lines = []
  adjustment_ok = False
  while font_size >= 16 and not adjustment_ok:
    font = pygame.font.Font(font_path, font_size)
    lines = []
    current_line = ""
    for word in words:
      test_line = current_line + (" " if current_line else "") + word
      test_surface = font.render(test_line, True, color)
      if test_surface.get_width() > max_width and current_line:
        lines.append(current_line)
        current_line = word
      else:
        current_line = test_line
    if current_line:
      lines.append(current_line)
    adjustment_ok = all(
        font.render(line, True, color).get_width() <= max_width for line in
        lines)
    if not adjustment_ok:
      font_size = int(font_size * 0.92)
  font = pygame.font.Font(font_path, font_size)
  surfaces = []
  for line in lines:
    surf = font.render(line, True, color)
    surfaces.append(surf)
  return surfaces


class BaseCombatModal(ABC):
  """Abstract base class for combat modals."""

  def __init__(self, font: FontType, rect: Rect, result_text: str = "") -> None:
    """
    Initializes the modal with font and rectangle.
    :param font: The font to use for text.
    :param rect: The rectangle defining the modal area.
    :param result_text: Initial result text to display.
    """
    self.__font: FontType = font
    self.__rect: Rect = rect
    self.__confirmed: bool = False
    self.__result_text: str = result_text
    self.__confirm_btn_rect: Rect | None = None
    self.__reset_btn_rect: Rect | None = None
    self.__init_buttons()

  def __init_buttons(self) -> None:
    """
    Initializes the Confirm and Reset button rectangles.
    """
    btn_w, btn_h = 100, 36
    margin = 10
    y_btn = self.__rect.y + self.__rect.height - btn_h - margin
    self.__confirm_btn_rect = pygame.Rect(
        self.__rect.x + self.__rect.width - btn_w - margin, y_btn, btn_w, btn_h)
    self.__reset_btn_rect = pygame.Rect(
        self.__rect.x + margin, y_btn, btn_w, btn_h)

  def get_confirmed(self) -> bool:
    """
    Returns whether the modal is active
    :return: True if confirmed, False otherwise.
    """
    return self.__confirmed

  def set_confirmed(self, value: bool) -> None:
    """
    Sets the confirmed state of the modal.
    :param value: True to confirm, False otherwise.
    """
    self.__confirmed = value

  def get_result_text(self) -> str:
    """
    Returns the result text to display
    :return: The result text.
    """
    return self.__result_text

  def set_result_text(self, text: str) -> None:
    """
    Sets the result text to display
    :param text: The result text.
    """
    self.__result_text = text

  def get_rect(self) -> Rect:
    """
    Returns the rectangle of the modal.
    :return: The modal rectangle.
    """
    return self.__rect

  def get_font(self) -> FontType:
    """
    Returns the font of the modal.
    :return: The modal font.
    """
    return self.__font

  def get_confirm_button(self) -> Rect:
    """
    Returns the confirm button rectangle.
    :return: The confirm button rectangle.
    """
    return self.__confirm_btn_rect

  def get_reset_button(self) -> Rect:
    """
    Returns the reset button rectangle.
    :return: The reset button rectangle.
    """
    return self.__reset_btn_rect

  @abstractmethod
  def draw(self, surface: Surface) -> None:
    """
    Draws the modal on the given surface.
    :param surface: The surface to draw on.
    """
    pass

  @abstractmethod
  def handle_combat_event(self, event: EventType) -> None:
    """
    Handles events for the modal (mouse, keyboard, etc).
    :param event: The event to handle.
    """
    pass

  @abstractmethod
  def get_player_answer(self) -> str:
    """
    Returns the player's constructed answer as a string.
    :return: The player's answer.
    """
    pass

  @abstractmethod
  def reset(self) -> None:
    """
    Resets the modal to its initial state.
    """
    pass

  def _draw_buttons(self, surface: Surface) -> None:
    """
    Draws the Confirm and Reset buttons.
    :param surface: The surface to draw on.
    """
    pygame.draw.rect(surface, Color.WORD_BG, self.__confirm_btn_rect)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.__confirm_btn_rect, 2)
    txt2 = self.__font.render("Confirmar", True, Color.TITLE_TEXT)
    txt2_rect = txt2.get_rect(center=self.__confirm_btn_rect.center)
    surface.blit(txt2, txt2_rect)

    pygame.draw.rect(surface, Color.WORD_BG, self.__reset_btn_rect)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.__reset_btn_rect, 2)
    txt = self.__font.render("Reiniciar", True, Color.TITLE_TEXT)
    txt_rect = txt.get_rect(center=self.__reset_btn_rect.center)
    surface.blit(txt, txt_rect)


class WordOrderingModal(BaseCombatModal):
  """Modal for word ordering questions with drag-and-drop."""

  def __init__(self, question_words: list[str], font: FontType, rect: Rect,
      result_text: str = "") -> None:
    """
    Initializes the word ordering modal.
    :param question_words: List of words to order.
    :param font: The font to use for text.
    :param rect: The rectangle defining the modal area.
    :param result_text: Initial result text to display.
    """
    super().__init__(font, rect, result_text)
    self.__original_words = list(question_words)
    self.__shuffled_words = list(self.__original_words)
    random.shuffle(self.__shuffled_words)
    self.__answer_words = []
    self.__dragging = None
    self.__word_rects = {"shuffled": [], "answer": []}
    self.__base_font = font
    self.__font_path = font.path if hasattr(font, "path") else None
    self.__shuffled_font = font
    self.__answer_font = font
    self.__update_word_rects()

  def __get_fit_font_and_layout(self, words: list[str], area_width: int,
      base_font: Font) -> tuple[FontType, int, int]:
    """
    Adjusts font size and layout to fit words within the given area width.
    :param words: List of words to fit.
    :param area_width: The width of the area to fit words into.
    :param base_font: The base font to start with.
    :return: A tuple containing the adjusted font, word width, and max words per row
    """
    font_size = base_font.get_height()
    margin = 10
    word_w = 90
    max_per_row = max(1, area_width // (word_w + margin))
    while len(words) > max_per_row and font_size > 16:
      font_size = int(font_size * 0.9)
      word_w = int(word_w * 0.9)
      max_per_row = max(1, area_width // (word_w + margin))
    font = pygame.font.Font(self.__font_path, font_size)
    return font, word_w, max_per_row

  def __update_word_rects(self) -> None:
    """
    Updates the rectangles for the words in both areas.
    """
    margin = 10
    title_height = 35
    area_width = self.get_rect().width - 2 * margin

    font_obj, word_w, max_per_row = self.__get_fit_font_and_layout(
        self.__shuffled_words, area_width, self.__base_font)
    word_h = font_obj.get_height() + 10
    self.__shuffled_font = font_obj
    self.__word_rects["shuffled"] = []
    for idx, word in enumerate(self.__shuffled_words):
      row = idx // max_per_row
      col = idx % max_per_row
      x = self.get_rect().x + margin + col * (word_w + margin)
      y = self.get_rect().y + margin + title_height + row * (word_h + margin)
      self.__word_rects["shuffled"].append(pygame.Rect(x, y, word_w, word_h))

    font_obj_ans, word_w_ans, max_per_row_ans = self.__get_fit_font_and_layout(
        self.__answer_words, area_width, self.__base_font)
    word_h_ans = font_obj_ans.get_height() + 10
    self.__answer_font = font_obj_ans
    self.__word_rects["answer"] = []
    for idx, word in enumerate(self.__answer_words):
      row = idx // max_per_row_ans
      col = idx % max_per_row_ans
      x = self.get_rect().x + margin + col * (word_w_ans + margin)
      y = self.get_rect().y + self.get_rect().height // 2 + row * (
          word_h_ans + margin)
      self.__word_rects["answer"].append(
          pygame.Rect(x, y, word_w_ans, word_h_ans))

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with words and buttons, ajustando desbordamiento.
    :param surface: The surface to draw on.
    """
    pygame.draw.rect(surface, Color.MODAL_BG, self.get_rect())
    title = self.get_font().render("Ordena las palabras:", True,
                                   Color.TITLE_TEXT)
    surface.blit(title, (self.get_rect().x + 10, self.get_rect().y + 5))
    for i, word in enumerate(self.__shuffled_words):
      rect: Rect = self.__word_rects["shuffled"][i]
      if word in self.__answer_words:
        pygame.draw.rect(surface, Color.WORD_BG_DISABLED, rect)
        pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
        txt = self.__shuffled_font.render(word, True, Color.WORD_TEXT_DISABLED)
      else:
        pygame.draw.rect(surface, Color.WORD_BG, rect)
        pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
        txt = self.__shuffled_font.render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (rect.x + 6, rect.y + 4))
    answer_area_rect = pygame.Rect(
        self.get_rect().x + 5,
        self.get_rect().y + self.get_rect().height // 2 - 8,
        self.get_rect().width - 10,
        48 + (len(self.__answer_words) // max(1, (
            self.get_rect().width // (90 + 10))) * 42)
    )
    pygame.draw.rect(surface, Color.ANSWER_AREA_BG, answer_area_rect)
    pygame.draw.rect(surface, Color.ANSWER_AREA_BORDER, answer_area_rect, 2)
    if not self.__answer_words:
      hint_txt = self.get_font().render("Arrastra aquí para formar la oración",
                                        True, Color.ANSWER_AREA_BORDER)
      hint_rect = hint_txt.get_rect(
          center=(answer_area_rect.centerx, answer_area_rect.y + 24))
      surface.blit(hint_txt, hint_rect)
    for i, word in enumerate(self.__answer_words):
      rect: Rect = self.__word_rects["answer"][i]
      pygame.draw.rect(surface, Color.ANSWER_WORD_BG, rect)
      pygame.draw.rect(surface, Color.WORD_BORDER, rect, 2)
      txt = self.__answer_font.render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (rect.x + 6, rect.y + 4))
    if self.__dragging:
      word, _, _ = self.__dragging
      mx, my = pygame.mouse.get_pos()
      drag_rect = pygame.Rect(mx - 45, my - 16, 90, 32)
      pygame.draw.rect(surface, Color.DRAG_WORD_BG, drag_rect)
      txt = self.get_font().render(word, True, Color.TITLE_TEXT)
      surface.blit(txt, (drag_rect.x + 6, drag_rect.y + 4))
    self._draw_buttons(surface)

  def handle_combat_event(self, event: EventType) -> None:
    """
    Handles mouse events for drag-and-drop and button clicks.
    :param event: The event to handle.
    """
    if event.type == MOUSEBUTTONDOWN:
      self._handle_mouse_down(event)
    elif event.type == MOUSEBUTTONUP and self.__dragging:
      self._handle_mouse_up(event)

  def _handle_mouse_down(self, event: EventType) -> None:
    """
    Handles mouse down events for starting drag or button clicks.
    :param event: the mouse event.
    """
    mx, my = event.pos
    if self.get_confirm_button().collidepoint(mx, my):
      self.set_confirmed(True)
    if self.get_reset_button().collidepoint(mx, my):
      self.__answer_words = []
      self.set_confirmed(False)
      self.__update_word_rects()
    for i, rect in enumerate(self.__word_rects["shuffled"]):
      word = self.__shuffled_words[i]
      if rect.collidepoint(mx, my) and word not in self.__answer_words:
        self.__dragging = (word, "shuffled", i)
    for i, rect in enumerate(self.__word_rects["answer"]):
      word = self.__answer_words[i]
      if rect.collidepoint(mx, my):
        self.__dragging = (word, "answer", i)

  def _handle_mouse_up(self, event: EventType) -> None:
    """
    Handles mouse up events for dropping dragged words.
    :param event: the mouse event.
    """
    mx, my = event.pos
    word, from_area, _ = self.__dragging
    answer_area = pygame.Rect(self.get_rect().x,
                              self.get_rect().y + self.get_rect().height // 2,
                              self.get_rect().width,
                              self.get_rect().height // 2)
    shuffled_area = pygame.Rect(self.get_rect().x, self.get_rect().y,
                                self.get_rect().width,
                                self.get_rect().height // 2)
    if from_area == "shuffled" and answer_area.collidepoint(mx, my):
      if word not in self.__answer_words:
        self.__answer_words.append(word)
    elif from_area == "answer" and shuffled_area.collidepoint(mx, my):
      if word in self.__answer_words:
        self.__answer_words.remove(word)
    self.__dragging = None
    self.__update_word_rects()

  def get_player_answer(self) -> str:
    """
    Returns the player's constructed answer as a string.
    :return: The player's answer.
    """
    return " ".join(self.__answer_words)

  def reset(self) -> None:
    """
    Resets the modal to its initial state.
    """
    self.__answer_words = []
    self.set_confirmed(False)
    self.__update_word_rects()


class MultipleChoiceModal(BaseCombatModal):
  """Modal for multiple choice questions."""

  def __init__(self, question: str, options: list[str], font: FontType,
      rect: Rect, result_text: str = "") -> None:
    """
    Initializes the multiple choice modal.
    :param question: The question to display.
    :param options: List of answer options.
    :param font: The font to use for text.
    :param rect: The rectangle defining the modal area.
    :param result_text: Initial result text to display.
    """
    super().__init__(font, rect, result_text)
    self.__question = question
    self.__options = options
    self.__selected_index = None
    self.__option_rects = []
    self.__font_path = font.path if hasattr(font, "path") else None
    self.__base_font = font
    self.__update_option_rects()

  def __update_option_rects(self) -> None:
    """
    Updates the rectangles for the options.
    """
    margin = 10
    option_h = 36
    option_w = self.get_rect().width - 2 * margin
    start_y = self.get_rect().y + 50
    self.__option_rects = []
    for i, _ in enumerate(self.__options):
      y = start_y + i * (option_h + margin)
      self.__option_rects.append(
          pygame.Rect(self.get_rect().x + margin, y, option_w, option_h))

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with question, options, and buttons.
    :param surface: The surface to draw on.
    """
    pygame.draw.rect(surface, Color.MODAL_BG, self.get_rect())
    title = self.get_font().render("Elige la respuesta correcta:", True,
                                   Color.TITLE_TEXT)
    surface.blit(title, (self.get_rect().x + 10, self.get_rect().y + 5))

    # Pregunta con ajuste de fuente y saltos de línea
    question_max_width = self.get_rect().width - 20
    question_surfaces = _render_text_multiline(
        self.__question,
        self.__font_path,
        self.__base_font.get_height(),
        question_max_width,
        Color.TITLE_TEXT
    )
    y_offset = self.get_rect().y + 30
    for surf in question_surfaces:
      surface.blit(surf, (self.get_rect().x + 10, y_offset))
      y_offset += surf.get_height() + 2

    # Opciones con ajuste de fuente y saltos de línea
    for i, option in enumerate(self.__options):
      rect: Rect = self.__option_rects[i]
      bg_color = Color.ANSWER_WORD_BG if self.__selected_index == i else Color.WORD_BG
      border_color = Color.ANSWER_AREA_BORDER if self.__selected_index == i else Color.WORD_BORDER
      pygame.draw.rect(surface, bg_color, rect)
      pygame.draw.rect(surface, border_color, rect, 2)
      option_surfaces = _render_text_multiline(
          option,
          self.__font_path,
          self.__base_font.get_height(),
          rect.width - 16,
          Color.TITLE_TEXT
      )
      opt_y = rect.y + 6
      for surf in option_surfaces:
        surface.blit(surf, (rect.x + 8, opt_y))
        opt_y += surf.get_height() + 2
      if self.__selected_index == i:
        pygame.draw.circle(surface, Color.ANSWER_AREA_BORDER,
                           (rect.right - 18, rect.centery), 10, 0)
    self._draw_buttons(surface)
    if self.get_result_text():
      result_color = Color.CORRECT_ANSWER_BG if "Correcto" in self.get_result_text() else Color.WRONG_ANSWER_BG
      result_surface = self.get_font().render(self.get_result_text(), True,
                                              result_color)
      result_x = self.get_rect().x + 10
      result_y = self.get_confirm_button().bottom + 10
      surface.blit(result_surface, (result_x, result_y))

  def handle_combat_event(self, event: EventType) -> None:
    """
    Handles mouse events for option selection and button clicks.
    :param event: The event to handle.
    """
    if event.type == MOUSEBUTTONDOWN:
      mx, my = event.pos
      if self.get_confirm_button().collidepoint(mx, my):
        self.set_confirmed(True)
        return
      if self.get_reset_button().collidepoint(mx, my):
        self.__selected_index = None
        self.set_confirmed(False)
        return
      for i, rect in enumerate(self.__option_rects):
        if rect.collidepoint(mx, my):
          self.__selected_index = i
          return

  def get_player_answer(self) -> str:
    """
    Returns the selected option as the player's answer.
    :return: The player's answer.
    """
    if self.__selected_index is not None:
      return self.__options[self.__selected_index]
    return ""

  def reset(self) -> None:
    """
    Resets the modal to initial state.
    """
    self.__selected_index = None
    self.set_confirmed(False)


class FillGapsModal(BaseCombatModal):
  """Modal for fill-in-the-blank questions with free text input."""

  def __init__(self, question: str, font: FontType, rect: Rect,
      result_text: str = "") -> None:
    """
    Initializes the fill-in-the-blank modal.
    :param question: The question to display with a blank.
    :param font: The font to use for text.
    :param rect: The rectangle defining the modal area.
    :param result_text: Initial result text to display.
    """
    super().__init__(font, rect, result_text)
    self.__question = question
    self.__input_text = ""
    self.__active_input = True
    self.__input_rect = pygame.Rect(
        self.get_rect().x + 20,
        self.get_rect().y + self.get_rect().height // 2 - 18,
        self.get_rect().width - 40,
        36
    )
    self.__cursor_visible = True
    self.__cursor_counter = 0
    self.__font_path = font.path if hasattr(font, "path") else None
    self.__base_font = font

  def draw(self, surface: Surface) -> None:
    """
    Draws the modal with a prompt, input box, and buttons.
    :param surface: The surface to draw on.
    """
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    pygame.draw.rect(surface, Color.MODAL_BG, self.get_rect(), border_radius=12)
    pygame.draw.rect(surface, Color.WORD_BORDER, self.get_rect(), 2,
                     border_radius=12)

    title = self.get_font().render("Completa el espacio en blanco:", True,
                                   Color.TITLE_TEXT)
    surface.blit(title, (self.get_rect().x + 20, self.get_rect().y + 18))

    # Pregunta con ajuste de fuente y saltos de línea
    question_max_width = self.get_rect().width - 40
    question_surfaces = _render_text_multiline(
        self.__question,
        self.__font_path,
        self.__base_font.get_height(),
        question_max_width,
        Color.TITLE_TEXT
    )
    y_offset = self.get_rect().y + 60
    for surf in question_surfaces:
      surface.blit(surf, (self.get_rect().x + 20, y_offset))
      y_offset += surf.get_height() + 2

    pygame.draw.rect(surface, Color.ANSWER_AREA_BG, self.__input_rect,
                     border_radius=8)
    pygame.draw.rect(surface, Color.ANSWER_AREA_BORDER, self.__input_rect, 2,
                     border_radius=8)
    input_display = self.__input_text
    if self.__active_input and self.__cursor_visible:
      input_display += "|"
    input_txt = self.get_font().render(input_display, True, Color.TITLE_TEXT)
    surface.blit(input_txt, (self.__input_rect.x + 8, self.__input_rect.y + 6))

    self._draw_buttons(surface)

    if self.get_result_text():
      result_color = Color.CORRECT_ANSWER_BG if "Correcto" in self.get_result_text() else Color.WRONG_ANSWER_BG
      result_surface = self.get_font().render(self.get_result_text(), True,
                                              result_color)
      result_x = self.get_rect().x + 20
      result_y = self.get_confirm_button().bottom + 14
      surface.blit(result_surface, (result_x, result_y))

    self.__cursor_counter += 1
    if self.__cursor_counter > 30:
      self.__cursor_visible = not self.__cursor_visible
      self.__cursor_counter = 0

  def handle_combat_event(self, event: EventType) -> None:
    """
    Handles mouse and keyboard events for text input and button clicks.
    :param event: The event to handle.
    """
    if event.type == MOUSEBUTTONDOWN:
      self._handle_mouse_event(event)
    elif event.type == pygame.KEYDOWN and self.__active_input:
      self._handle_keyboard_event(event)

  def _handle_mouse_event(self, event: EventType) -> None:
    """
    Handles mouse events for input box activation and button clicks.
    :param event: the mouse event.
    """
    mx, my = event.pos
    if self.__input_rect.collidepoint(mx, my):
      self.__active_input = True
    else:
      self.__active_input = False
    if self.get_confirm_button().collidepoint(mx, my):
      self.set_confirmed(True)
      return
    if self.get_reset_button().collidepoint(mx, my):
      self.__input_text = ""
      self.set_result_text("")
      self.set_confirmed(False)

  def _handle_keyboard_event(self, event: EventType) -> None:
    """
    Handles keyboard events for text input.
    :param event: the keyboard event.
    """
    if event.key == pygame.K_BACKSPACE:
      self.__input_text = self.__input_text[:-1]
    elif event.key == pygame.K_RETURN:
      self.set_confirmed(True)
    else:
      char = event.unicode
      if len(char) == 1 and len(self.__input_text) < 40:
        self.__input_text += char

  def get_player_answer(self) -> str:
    """
    Returns the user's input as the answer.
    :return: The player's answer.
    """
    return self.__input_text.strip()

  def reset(self) -> None:
    """
    Resets the modal to initial state.
    """
    self.__active_input = True
    self.__cursor_visible = True
    self.__input_text = ""
    self.set_confirmed(False)
    self.set_result_text("")
