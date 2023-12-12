#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
from typing import Callable, Awaitable

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from config import TOKEN
from model.menu_state import MenuState
from model.user import User
from repository.repository_inst import user_repository

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def home_menu_handler(user: User, update: Update):
    if update.message.text == '/quiz':
        user.question_index = 0
        user.menu_state = MenuState.QUIZ
        await update.message.reply_text(f"{update.message.text}, {user.question_index+1}")


async def quiz_menu_handler(user: User, update: Update):
    await update.message.reply_text(f"{update.message.text}, {user.question_index + 1}")
    if user.question_index == 3:
        user.question_index = 0
        user.menu_state = MenuState.HOME
    else:
        user.question_index += 1


menu_state_handlers: dict[MenuState, Callable[[User, Update], Awaitable[None]]] = {
    MenuState.HOME: home_menu_handler,
    MenuState.QUIZ: quiz_menu_handler,
}


async def message_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    user = await user_repository.read_or_create(user_id)
    if user.menu_state in menu_state_handlers:
        await menu_state_handlers[user.menu_state](user, update)
    await user_repository.update(user)


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
