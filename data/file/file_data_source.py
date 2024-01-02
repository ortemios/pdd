class FileDataSource:

    async def write_json(self, path: str, data: dict):
        raise NotImplementedError()

    async def read_json(self, path: str) -> dict:
        raise NotImplementedError()

    async def list_dir(self, path: str) -> list[str]:
        raise NotImplementedError()

    async def generate_link(self, path: str) -> str:
        raise NotImplementedError()