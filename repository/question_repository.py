from model.question import Question


class QuestionRepository:
    async def get_question(self, category_id: str, index: int) -> Question:
        raise NotImplementedError()


question_repository = QuestionRepository()
