import json


class DataSource:

    BASE_DIR = '_storage'

    def save_object(self, name: str, uid: int, obj: dict):
        with open(f'{self.BASE_DIR}/{name}/{uid}.json', 'w') as f:
            json.dump(obj, f)

    def read_object(self, name: str, uid: int) -> dict:
        with open(f'{self.BASE_DIR}/{name}/{uid}.json', 'r') as f:
            return json.load(f)
