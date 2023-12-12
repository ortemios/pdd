from typing import Optional

from mappers.question_mapper import QuestionMapper
from model.question import Question
from data.data_source_inst import data_source
from repository.category_repository import CategoryRepository


class QuestionRepository:

    async def get_question(self, category_id: str, index: int) -> Optional[Question]:
        try:
            category = await CategoryRepository().get_category(category_id)
            questions = await data_source.read_json(f'{category.path}.json')
            json = questions[index - 1]
            return QuestionMapper().from_json(json)
        except:
            return None


question_repository = QuestionRepository()
