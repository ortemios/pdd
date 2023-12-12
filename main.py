#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
from typing import Callable, Awaitable

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from config import TOKEN
from model.menu_state import MenuState
from model.question import Question
from model.user import User
from repository.repository_inst import user_repository, category_repository, question_repository

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


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
        for index, answer in enumerate(question.answers):
            keyboard.append([InlineKeyboardButton(
                f'{index+1}. {answer}',
                callback_data=f'{index}',
            )])
        await send_message(
            update,
            text=question.text,
            photo_url=question.image,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def home_menu_handler(user: User, update: Update):
    query = update.callback_query
    message = update.message

    if query and query.data.startswith('/quiz'):
        text = query.data
        await query.answer()
        args = text.split()[1:]
        if len(args) == 0:
            await send_message(update, text="Укажите категорию")
        else:
            category = await category_repository.get_category(args[0])
            user.question_index = 0
            user.menu_state = MenuState.QUIZ
            user.quiz_category_id = category.id
            await send_question(user, update)

    if message and message.text == '/categories':
        keyboard = list(map(
            lambda c: [InlineKeyboardButton(
                c.title,
                callback_data=f'/quiz {c.id}',
            )],
            await category_repository.get_categories(),
        ))
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(update, "Выберите категорию: ", reply_markup=reply_markup)


async def quiz_menu_handler(user: User, update: Update):
    if update.callback_query:
        answer_index = update.callback_query.data
        question = await question_repository.get_question(
            user.quiz_category_id,
            user.question_index
        )
        if answer_index == str(question.correct_answer_index):
            await send_message(update, text=f'Правильно!')
        else:
            await send_message(
                update,
                text=f'''Неправильный ответ.
Номер правильного ответа: {question.correct_answer_index+1}.
{question.answer_tip}'''
            )
        if user.question_index == 2:
            await send_message(
                update,
                text='Тест завершен!'
            )
            user.menu_state = MenuState.HOME
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
    if user.menu_state in menu_state_handlers:
        await menu_state_handlers[user.menu_state](user, update)
    await user_repository.update(user)


async def button_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await message_handler(update, _)


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
