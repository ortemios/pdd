from repository.category_repository import CategoryRepository
from repository.question_repository import QuestionRepository
from repository.user_repository.db_user_repository import DbUserRepository
from repository.user_repository.user_repository import UserRepository


user_repository: UserRepository = DbUserRepository()
category_repository = CategoryRepository()
question_repository = QuestionRepository()
