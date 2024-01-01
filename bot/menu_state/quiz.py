from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.menu_state.menu_state_inst import MenuStateInst
from model.menu_state import MenuState
from repository.repository_inst import question_repository


class QuizMenuState(MenuStateInst):

    async def send_question(self):
        question = await question_repository.get_question(
            self.user.quiz_category_id,
            self.user.question_index
        )
        if self.update.callback_query:
            keyboard = []
            answers = []
            for index, answer in enumerate(question.answers):
                keyboard.append([InlineKeyboardButton(
                    str(index + 1),
                    callback_data=f'{index}',
                )])
                answers.append(f'{index + 1}. {answer}')
            keyboard.append([InlineKeyboardButton(
                '🛑Прервать тест',
                callback_data=f'quiz stop',
            )])
            text = f'❓Вопрос {self.user.question_index + 1}/{question.total_questions}\n\n' + \
                   f'{question.text}\n\n' + \
                   '\n'.join(answers)
            await self.send_message(
                text=text,
                photo_url=question.image,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    async def on_enter(self):
        await self.send_question()

    async def on_update(self):
        if self.update.callback_query:
            answer = self.update.callback_query.data
            question = await question_repository.get_question(
                self.user.quiz_category_id,
                self.user.question_index
            )
            if answer.isdigit():
                if answer == str(question.correct_answer_index):
                    await self.send_message(text=f'✅️️Правильно!')
                else:
                    await self.send_message(
                        text=f'❌Неправильный ответ.\n' +
                             f'Номер правильного ответа: {question.correct_answer_index + 1}.\n' +
                             f'{question.answer_tip}'
                    )
            if self.user.question_index + 1 >= question.total_questions or \
                    answer == 'quiz stop':
                await self.send_message(
                    text='🏁Тест завершен!'
                )
                self.user.menu_state = MenuState.HOME
            else:
                self.user.question_index += 1
                await self.send_question()
