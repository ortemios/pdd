from model.menu_state import MenuState
from model.user import User


class UserMapper:
    def to_json(self, user: User) -> dict:
        return {
            'id': user.id,
            'menu_state': user.menu_state.value,
            'quiz_category_id': user.quiz_category_id,
            'question_index': user.question_index,
            'scheduled_category_id': user.scheduled_category_id,
            'scheduled_frequency': user.scheduled_frequency,
        }

    def from_json(self, json: dict) -> User:
        user = User()
        user.id = json['id']
        user.menu_state = MenuState(json['menu_state'])
        user.quiz_category_id = json['quiz_category_id']
        user.question_index = json['question_index']
        user.scheduled_category_id = json['scheduled_category_id']
        user.scheduled_frequency = json['scheduled_frequency']
        return user

    def from_sql(self, row) -> User:
        user = User()
        user.id = row[0]
        user.menu_state = MenuState(row[1])
        user.quiz_category_id = row[2]
        user.question_index = row[3]
        user.scheduled_category_id = row[4]
        user.scheduled_frequency = row[5]
        return user
