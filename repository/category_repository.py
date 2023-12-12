import re
from typing import Optional

from model.category_group import CategoryGroup
from model.quiz_category import QuizCategory
from data.data_source_inst import data_source


class CategoryRepository:

    async def get_category(self, category_id: str) -> Optional[QuizCategory]:
        tokens = category_id.split('/')
        group_id = '/'.join(tokens[:-1])
        index = int(tokens[-1])
        for i, name in enumerate(await data_source.list_dir(group_id)):
            if i == index:
                return self._id_to_category(group_id, name, index)

    async def get_category_groups(self) -> list[CategoryGroup]:
        return [
            CategoryGroup(id='questions/A_B/tickets', title='A/B, варианты'),
            CategoryGroup(id='questions/C_D/tickets', title='C/D, варианты'),
            CategoryGroup(id='questions/A_B/topics', title='A/B, темы'),
            CategoryGroup(id='questions/C_D/topics', title='C/D, темы'),
        ]

    async def get_categories(self, group_id: str) -> list[QuizCategory]:
        def atoi(text):
            return int(text) if text.isdigit() else text

        def natural_keys(item: QuizCategory):
            return [atoi(c) for c in re.split(r'(\d+)', item.path)]

        path = group_id
        categories: list[QuizCategory] = [
            self._id_to_category(group_id, name, index)
            for index, name in enumerate(await data_source.list_dir(path))
        ]
        return list(sorted(categories, key=natural_keys))[1:]

    def _id_to_category(self, group_id: str, name: str, index: int) -> QuizCategory:
        path = f"{group_id}/{name.split('.')[0]}"
        tokens = path.split('/')
        prefix = {
            'A_B': 'A/B',
            'C_D': 'C/D'
        }[tokens[1]]
        suffix = tokens[-1].split('.')[0]

        category = QuizCategory()
        category.id = f'{group_id}/{str(index)}'
        category.path = path
        category.title = f'{prefix}: {suffix}'
        return category


category_repository = CategoryRepository()
