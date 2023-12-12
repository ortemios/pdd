from model.menu_state import MenuState
from model.user import User


class UserRepository:

    _users: dict[int, User] = {}

    def create(self, user_id: int) -> User:
        user = User()
        user.id = user_id
        user.menu_state = MenuState.HOME
        user.quiz_category = None
        user.question_index = 0
        user.scheduled_category = None
        user.scheduled_frequency = 0
        self._users[user_id] = user
        return user

    def read_or_create(self, user_id: int) -> User:
        if user_id not in self._users:
            return self.create(user_id)
        else:
            return self._users[user_id]

    def update(self, user: User):
        self._users
