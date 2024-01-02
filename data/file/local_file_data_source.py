import json
import os

from data.file.file_data_source import FileDataSource


class LocalFileDataSource(FileDataSource):

    BASE_DIR = 'pdd_russia'

    def _path(self, path: str) -> str:
        return f'{self.BASE_DIR}/{path}'

    async def write_json(self, path: str, data: dict):
        with open(self._path(path), 'w') as f:
            json.dump(data, f)

    async def read_json(self, path: str) -> dict:
        with open(self._path(path), 'r') as f:
            return json.load(f)

    async def list_dir(self, path: str) -> list[str]:
        return list(filter(
            lambda item: item,
            os.listdir(self._path(path))
        ))

    async def generate_link(self, path: str) -> str:
        return f'https://raw.githubusercontent.com/etspring/pdd_russia/master/{path}?raw=true'

