from typing import Optional

from mappers.question_mapper import QuestionMapper
from model.question import Question
from data.data_source_inst import file_data_source
from repository.category_repository import CategoryRepository


class QuestionRepository:

    async def get_question(self, category_id: str, index: int) -> Optional[Question]:
        try:
            category = await CategoryRepository().get_category(category_id)
            questions = await file_data_source.read_json(f'{category.path}.json')
            json = questions[index - 1]
            question = QuestionMapper().from_json(json)
            question.total_questions = len(questions)
            if question.image:
                question.image = await file_data_source.generate_link(question.image)
            return question
        except Exception as e:
            print(e)
            return None


question_repository = QuestionRepository()
