#!/usr/bin/env python
# pylint: disable=unused-argument
import asyncio
import enum
import json
import logging
import math
import time
from threading import Thread
from typing import Callable, Awaitable

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from config import TOKEN
from model.menu_state import MenuState
from model.user import User
from repository.repository_inst import user_repository, category_repository, question_repository

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class ButtonCallbacks(enum.Enum):
    QUIZ = 'quiz'
    CATEGORIES = 'categories'
    CATEGORY_GROUP = 'category_group'
    SCHEDULE_CATEGORIES = 'schedule_categories'
    SCHEDULE_CATEGORY_GROUP = 'schedule_category_group'
    SCHEDULE_CATEGORY_TIMINGS = 'schedule_category_timings'
    SCHEDULE_QUIZ = 'schedule_quiz'
    SCHEDULE_CANCEL = 'schedule_cancel'


async def send_message(
        update: Update,
        text: str = '',
        photo_url: str = '',
        reply_markup: InlineKeyboardMarkup = None):
    if photo_url:
        await update.get_bot().send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_url
        )
    await update.get_bot().send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )


async def send_question(user: User, update: Update):
    question = await question_repository.get_question(
        user.quiz_category_id,
        user.question_index
    )
    if update.callback_query:
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
        text = f'❓Вопрос {user.question_index + 1}/{question.total_questions}\n\n' + \
               f'{question.text}\n\n' + \
               '\n'.join(answers)
        await send_message(
            update,
            text=text,
            photo_url=question.image,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def send_main_menu(update: Update, user: User):
    keyboard = [
        [
            InlineKeyboardButton(
                f'📖Категории вопросов',
                callback_data=ButtonCallbacks.CATEGORIES.value,
            ),
        ],
        [
            InlineKeyboardButton(
                f'📖Запланировать рассылку',
                callback_data=ButtonCallbacks.SCHEDULE_CATEGORIES.value,
            ),
        ],
    ]
    if user.scheduled_frequency > 0 and user.scheduled_category_id:
        keyboard[-1].append(
            InlineKeyboardButton(
                f'📖Отменить рассылку',
                callback_data=ButtonCallbacks.SCHEDULE_CANCEL.value,
            )
        )
    await send_message(
        update,
        text='Выберите опцию:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def send_category_groups(update: Update, callback_name: str):
    keyboard = list(map(
        lambda c: [InlineKeyboardButton(
            c.title,
            callback_data=f'{callback_name} {c.id}',
        )],
        await category_repository.get_category_groups(),
    ))
    await send_message(
        update,
        "Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def send_categories(update: Update, callback_name: str):
    args = update.callback_query.data.split()[1:]
    if len(args) < 1:
        await send_message(update, text="Укажите категорию")
    else:
        group_id = args[0]
        keyboard = list(map(
            lambda c: [InlineKeyboardButton(
                c.title,
                callback_data=f'{callback_name} {c.id}',
            )],
            await category_repository.get_categories(group_id=group_id),
        ))
        await send_message(
            update,
            "Выберите вариант:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def send_schedule_timings(update: Update, callback_name: str):
    args = update.callback_query.data.split()[1:]
    if len(args) < 1:
        await send_message(update, text="Укажите ID варианта")
    else:
        category_id = args[0]
        keyboard = list(map(
            lambda item: [InlineKeyboardButton(
                f'{item}',
                callback_data=f'{callback_name} {category_id} {item}',
            )],
            range(1, 11)
        ))
        await send_message(
            update,
            "Выберите число отправок в сутки:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def send_schedule_quiz(update: Update, user: User):
    args = update.callback_query.data.split()[1:]
    if len(args) < 2 or not args[1].isdigit():
        await send_message(update, text="Укажите ID варианта и частоту отправки")
    else:
        category_id = args[0]
        frequency = int(args[1])
        user.scheduled_category_id = category_id
        user.scheduled_frequency = frequency
        await send_message(
            update,
            "Отправка запланирована"
        )
        await send_main_menu(update, user)


async def send_schedule_cancel(update: Update, user: User):
    user.scheduled_category_id = ''
    user.scheduled_frequency = 0
    await send_message(
        update,
        "Отправка отменена"
    )
    await send_main_menu(update, user)


async def home_menu_handler(user: User, update: Update):
    query = update.callback_query
    if query:
        if query.data.startswith(ButtonCallbacks.QUIZ.value):
            args = query.data.split()[1:]
            if len(args) < 1:
                await send_message(update, text="Укажите категорию")
            else:
                user.question_index = 0
                user.menu_state = MenuState.QUIZ
                user.quiz_category_id = args[0]
                await send_question(user, update)

        if query.data == ButtonCallbacks.CATEGORIES.value:
            await send_category_groups(update, ButtonCallbacks.CATEGORY_GROUP.value)

        if query.data.startswith(ButtonCallbacks.CATEGORY_GROUP.value):
            await send_categories(update, ButtonCallbacks.QUIZ.value)

        if query.data == ButtonCallbacks.SCHEDULE_CATEGORIES.value:
            await send_category_groups(update, ButtonCallbacks.SCHEDULE_CATEGORY_GROUP.value)

        if query.data.startswith(ButtonCallbacks.SCHEDULE_CATEGORY_GROUP.value):
            await send_categories(update, ButtonCallbacks.SCHEDULE_CATEGORY_TIMINGS.value)

        if query.data.startswith(ButtonCallbacks.SCHEDULE_CATEGORY_TIMINGS.value):
            await send_schedule_timings(update, ButtonCallbacks.SCHEDULE_QUIZ.value)

        if query.data.startswith(ButtonCallbacks.SCHEDULE_QUIZ.value):
            await send_schedule_quiz(update, user)

        if query.data == ButtonCallbacks.SCHEDULE_CANCEL.value:
            await send_schedule_cancel(update, user)


async def quiz_menu_handler(user: User, update: Update):
    if update.callback_query:
        answer = update.callback_query.data
        question = await question_repository.get_question(
            user.quiz_category_id,
            user.question_index
        )
        if answer.isdigit():
            if answer == str(question.correct_answer_index):
                await send_message(update, text=f'✅️️Правильно!')
            else:
                await send_message(
                    update,
                    text=f'❌Неправильный ответ.\n' +
                         f'Номер правильного ответа: {question.correct_answer_index + 1}.\n' +
                         f'{question.answer_tip}'
                )
        if user.question_index + 1 >= question.total_questions or \
                answer == 'quiz stop':
            await send_message(
                update,
                text='🏁Тест завершен!'
            )
            user.menu_state = MenuState.HOME
            await send_main_menu(update, user)
        else:
            user.question_index += 1
            await send_question(user, update)


menu_state_handlers: dict[MenuState, Callable[[User, Update], Awaitable[None]]] = {
    MenuState.HOME: home_menu_handler,
    MenuState.QUIZ: quiz_menu_handler,
}


async def message_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = await user_repository.read_or_create(user_id)

    if update.message and update.message.text == '/start':
        await send_main_menu(update, user)

    if user.menu_state in menu_state_handlers:
        await menu_state_handlers[user.menu_state](user, update)
    await user_repository.update(user)


async def button_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await message_handler(update, _)


def create_app() -> Application:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    application.add_handler(CallbackQueryHandler(button_handler))
    return application


async def handler(event, context):
    application = create_app()
    await application.initialize()
    await application.start()

    update = json.loads(event['body'])
    print(update)

    await application.update_queue.put(Update.de_json(data=update, bot=application.bot))

    await application.stop()
    return {
        'statusCode': 200,
        'body': ''
    }


def main() -> None:
    application = create_app()
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
