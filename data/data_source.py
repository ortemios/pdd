import random


class DataSource:

    name: int = random.randint(0, 1000)

    async def write_json(self, path: str, data: dict):
        raise NotImplementedError()

    async def read_json(self, path: str) -> dict:
        raise NotImplementedError()

    async def list_dir(self, path: str) -> list[str]:
        raise NotImplementedError()
