from typing import Optional

from mappers.user_mapper import UserMapper
from model.menu_state import MenuState
from model.user import User
from data.data_source_inst import pg_data_source
from repository.user_repository.user_repository import UserRepository


class DbUserRepository(UserRepository):
    _users: dict[int, User] = {}

    async def create(self, user_id: int) -> User:
        cur = pg_data_source.get_cursor()
        cur.execute('INSERT INTO users '
                    '(menu_state, quiz_category_id, question_index, scheduled_category_id, scheduled_frequency) '
                    'VALUES (%s, %d, %d, %d, %d)',
                    (MenuState.HOME.value, None, 0, 0, 0)
                    )
        cur.commit()
        cur.close()
        return await self.read(user_id)

    async def read(self, user_id: int) -> Optional[User]:
        try:
            cur = pg_data_source.get_cursor()
            cur.execute("SELECT * FROM users WHERE id=%s", user_id)
            row = cur.fetchone()
            cur.close()
            return UserMapper().from_sql(row)
        except Exception as e:
            return None

    async def update(self, user: User):
        cur = pg_data_source.get_cursor()
        cur.execute('UPDATE users SET'
                    'menu_state=%s'
                    'quiz_category_id=%s'
                    'question_index=%s'
                    'scheduled_category_id=%s'
                    'quiz_category_id=%s'
                    'quiz_category_id=%s'
                    'WHERE id=%s',
                    (user.menu_state,
                     user.quiz_category_id,
                     user.question_index,
                     user.scheduled_category_id,
                     user.scheduled_frequency,
                     user.id)
                    )
        cur.commit()

    async def read_all(self) -> list[User]:
        cur = pg_data_source.get_cursor()
        cur.execute("SELECT * FROM users")
        users = [UserMapper().from_sql(row) for row in cur]
        cur.close()
        return users
