from model.quiz_category import QuizCategory


class CategoryRepository:

    async def get_category(self, category_id: str) -> QuizCategory:
        raise NotImplementedError()


category_repository = CategoryRepository()
