from model.menu_state import MenuState
from model.quiz_category import QuizCategory


class User:
    id: int
    menu_state: MenuState
    quiz_category_id: int
    question_index: int
    scheduled_category_id: int
    scheduled_frequency: int
