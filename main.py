#!/usr/bin/env python
# pylint: disable=unused-argument
import json
import logging
from typing import Callable

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from bot.menu_state.home import HomeMenuState
from bot.menu_state.menu_state_inst import MenuStateInst
from bot.menu_state.quiz import QuizMenuState
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


menu_state_handlers: dict[MenuState, Callable[[], MenuStateInst]] = {
    MenuState.HOME: lambda: HomeMenuState(),
    MenuState.QUIZ: lambda: QuizMenuState(),
}


def get_menu_handler(user: User, update: Update) -> MenuStateInst:
    handler_inst = menu_state_handlers[user.menu_state]()
    handler_inst.update = update
    handler_inst.user = user
    return handler_inst


async def message_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = await user_repository.read_or_create(user_id)

    if update.message and update.message.text == '/start':
        user.menu_state = MenuState.HOME
        await user_repository.update(user)
        await get_menu_handler(user, update).on_enter()
    else:
        old_state = user.menu_state
        if user.menu_state in menu_state_handlers:
            await get_menu_handler(user, update).on_update()
        await user_repository.update(user)
        new_state = user.menu_state
        if old_state != new_state:
            await get_menu_handler(user, update).on_enter()


async def button_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await message_handler(update, _)


def create_app() -> Application:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    application.add_handler(CallbackQueryHandler(button_handler))
    return application


async def handler(event, _):
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
