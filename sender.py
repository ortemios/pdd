import math
import time

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application

import config
from model.menu_state import MenuState
from repository.repository_inst import user_repository
from res import strings


async def handler(event, context):
    hour = 3600
    period = 24*hour
    interval = 1*hour
    now = time.time() % period
    index = int(now / interval)
    total = int(period / interval)

    application = Application.builder().token(config.TOKEN).build()
    await application.initialize()
    await application.start()

    users = await user_repository.read_all()
    for user in users:
        if user.scheduled_frequency > 0 and user.scheduled_category_id and user.menu_state == MenuState.HOME:
            n = math.ceil(total / user.scheduled_frequency)
            if index % n >= 0:
                await application.bot.send_message(
                    chat_id=user.id,
                    text=strings.time_to_solve,
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                text=strings.start,
                                callback_data=f'quiz {user.scheduled_category_id}'
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text=strings.cancel_sending,
                                callback_data='schedule_cancel'
                            )
                        ]
                    ])
                )
    await application.stop()
    return {
        'statusCode': 200,
        'body': ''
    }
