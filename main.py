#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from typing import Callable, Awaitable

from telegram import ForceReply, Update, Message
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from model.menu_state import MenuState
from model.user import User
from repository.user_repository import UserRepository

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

user_repository = UserRepository()


async def home_menu_handler(user: User, update: Update):
    await update.message.reply_text(f"{update.message.text}, {user.question_index}")
    user.question_index += 1


handlers: dict[MenuState, Callable[[User, Update], Awaitable[None]]] = {
    MenuState.HOME: home_menu_handler,
}


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user_id = update.message.chat_id
    user = user_repository.read_or_create(user_id)
    if user.menu_state in handlers:
        await handlers[user.menu_state](user, update)
    user_repository.update(user)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6912350070:AAEAgyBPcszROt6HJehEviwTsOftIpEJ8JM").build()

    application.add_handler(MessageHandler(filters.TEXT, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
