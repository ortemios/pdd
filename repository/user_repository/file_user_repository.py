from typing import Optional

from data.data_source_inst import file_data_source
from mappers.user_mapper import UserMapper
from model.menu_state import MenuState
from model.user import User
from repository.user_repository.user_repository import UserRepository


class FileUserRepository(UserRepository):

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
                await file_data_source.read_json(path=self._path(user_id))
            )
        except Exception as e:
            return None

    async def update(self, user: User):
        await file_data_source.write_json(
            path=self._path(user.id),
            data=UserMapper().to_json(user)
        )

    async def read_all(self) -> list[User]:
        return [await self.read(int(name.split('.')[0])) for name in await file_data_source.list_dir('users')]

