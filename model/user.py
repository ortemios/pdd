from model.menu_state import MenuState
from model.quiz_category import QuizCategory


class User:
    id: int
    menu_state: MenuState
    quiz_category: QuizCategory
    question_index: int
    scheduled_category: QuizCategory
    scheduled_frequency: int
