import json
import os

from data.data_source import DataSource


class LocalDataSource(DataSource):

    BASE_DIR = 'pdd_russia'

    async def write_json(self, path: str, data: dict):
        with open(f'{self.BASE_DIR}/{path}', 'w') as f:
            json.dump(data, f)

    async def read_json(self, path: str) -> dict:
        with open(f'{self.BASE_DIR}/{path}', 'r') as f:
            return json.load(f)

    async def list_dir(self, path: str) -> list[str]:
        return list(sorted(os.listdir(path)))
