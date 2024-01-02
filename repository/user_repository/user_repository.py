from typing import Optional

from model.user import User


class UserRepository:

    async def create(self, user_id: int) -> User:
        pass

    async def read(self, user_id: int) -> Optional[User]:
        pass

    async def update(self, user: User):
        pass

    async def read_all(self) -> list[User]:
        pass

    async def read_or_create(self, user_id: int) -> User:
        user = await self.read(user_id)
        if user is None:
            user = await self.create(user_id)
        return user
