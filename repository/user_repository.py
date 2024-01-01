from typing import Optional

from mappers.user_mapper import UserMapper
from model.menu_state import MenuState
from model.user import User
from data.data_source_inst import data_source


class UserRepository:

    _users: dict[int, User] = {}

    def _path(self, user_id: int) -> str:
        return f'users/{user_id}.json'

    async def create(self, user_id: int) -> User:
        user = User()
        user.id = user_id
        user.menu_state = MenuState.HOME
        user.quiz_category_id = None
        user.question_index = 0
        user.scheduled_category_id = None
        user.scheduled_frequency = 0
        await self.update(user)
        return user

    async def read(self, user_id: int) -> Optional[User]:
        try:
            return UserMapper().from_json(
                await data_source.read_json(path=self._path(user_id))
            )
        except Exception as e:
            return None

    async def read_or_create(self, user_id: int) -> User:
        user = await self.read(user_id)
        if user is None:
            user = await self.create(user_id)
        return user

    async def update(self, user: User):
        await data_source.write_json(
            path=self._path(user.id),
            data=UserMapper().to_json(user)
        )

    async def read_all(self) -> list[User]:
        return [await self.read(int(name.split('.')[0])) for name in await data_source.list_dir('users')]


