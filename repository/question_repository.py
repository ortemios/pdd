from typing import Optional

from mappers.question_mapper import QuestionMapper
from model.question import Question
from data.data_source_inst import data_source


class QuestionRepository:

    async def get_question(self, category_id: str, index: int) -> Optional[Question]:
        try:
            questions = await data_source.read_json(f'{category_id}.json')
            json = questions[index - 1]
            return QuestionMapper().from_json(json)
        except:
            return None


question_repository = QuestionRepository()
