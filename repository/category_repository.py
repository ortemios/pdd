import re

from model.quiz_category import QuizCategory
from data.data_source_inst import data_source


class CategoryRepository:

    async def get_category(self, category_id: str) -> QuizCategory:
        return self._id_to_category(category_id)

    async def get_categories(self) -> list[QuizCategory]:
        def atoi(text):
            return int(text) if text.isdigit() else text

        def natural_keys(item: QuizCategory):
            return [atoi(c) for c in re.split(r'(\d+)', item.id)]

        paths = [
            'questions/A_B/tickets/',
            #'questions/A_B/topics/',
            # 'questions/C_D/tickets/',
            # 'questions/C_D/topics/',
        ]
        categories: list[QuizCategory] = []
        for path in paths:
            categories += list(map(
                lambda name: self._id_to_category(path + name.split('.')[0]),
                await data_source.list_dir(path)
            ))
        return list(sorted(categories, key=natural_keys))[1:]

    def _id_to_category(self, category_id: str) -> QuizCategory:
        tokens = category_id.split('/')
        prefix = {
            'A_B': 'A/B',
            'C_D': 'C/D'
        }[tokens[1]]
        suffix = tokens[-1].split('.')[0]

        category = QuizCategory()
        category.id = category_id
        category.title = f'{prefix}: {suffix}'
        return category


category_repository = CategoryRepository()
