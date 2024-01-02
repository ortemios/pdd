from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.buttons.button_handler import ButtonCallback, ButtonHandler
from bot.menu_state.menu_state_inst import MenuStateInst
from model.menu_state import MenuState
from repository.repository_inst import category_repository
from res import strings


class HomeMenuState(MenuStateInst):
    button_handler = ButtonHandler()

    def __init__(self):
        self.button_handler.add_handler(ButtonCallback.QUIZ, lambda args: self.start_quiz(args))
        self.button_handler.add_handler(ButtonCallback.CATEGORIES,
                                        lambda args: self.send_category_groups(ButtonCallback.CATEGORY_GROUP))
        self.button_handler.add_handler(ButtonCallback.CATEGORY_GROUP,
                                        lambda args: self.send_categories(args, ButtonCallback.QUIZ))
        self.button_handler.add_handler(ButtonCallback.SCHEDULE_CATEGORIES,
                                        lambda args: self.send_category_groups(ButtonCallback.SCHEDULE_CATEGORY_GROUP))
        self.button_handler.add_handler(ButtonCallback.SCHEDULE_CATEGORY_GROUP, lambda args: self.send_categories(args,
                                                                                                                  ButtonCallback.SCHEDULE_CATEGORY_TIMINGS))
        self.button_handler.add_handler(ButtonCallback.SCHEDULE_CATEGORY_TIMINGS,
                                        lambda args: self.send_schedule_timings(args, ButtonCallback.SCHEDULE_QUIZ))
        self.button_handler.add_handler(ButtonCallback.SCHEDULE_QUIZ, lambda args: self.send_schedule_quiz(args))
        self.button_handler.add_handler(ButtonCallback.SCHEDULE_CANCEL, lambda args: self.send_schedule_cancel())

    async def on_enter(self):
        await self.send_main_menu()

    async def on_update(self):
        await self.button_handler.handle(self.update)

    async def start_quiz(self, args: list[Any]):
        if len(args) < 1:
            await self.send_message(text=strings.specify_category)
        else:
            self.user.question_index = 0
            self.user.menu_state = MenuState.QUIZ
            self.user.quiz_category_id = str(args[0])

    async def send_main_menu(self):
        keyboard = [
            [
                InlineKeyboardButton(
                    strings.question_categories,
                    callback_data=ButtonCallback.CATEGORIES.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    strings.schedule_sending,
                    callback_data=ButtonCallback.SCHEDULE_CATEGORIES.value,
                ),
            ],
        ]
        if self.user.scheduled_frequency > 0 and self.user.scheduled_category_id:
            keyboard[-1].append(
                InlineKeyboardButton(
                    strings.cancel_sending,
                    callback_data=ButtonCallback.SCHEDULE_CANCEL.value,
                )
            )
        await self.send_message(
            text=strings.choose_option,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def send_category_groups(self, callback_id: ButtonCallback):
        keyboard = list(map(
            lambda c: [InlineKeyboardButton(
                c.title,
                callback_data=f'{callback_id.value} {c.id}',
            )],
            await category_repository.get_category_groups(),
        ))
        await self.send_message(
            strings.choose_category,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def send_categories(self, args: list[Any], callback_id: ButtonCallback):
        if len(args) < 1:
            await self.send_message(text=strings.choose_category)
        else:
            group_id = str(args[0])
            keyboard = list(map(
                lambda c: [InlineKeyboardButton(
                    c.title,
                    callback_data=f'{callback_id.value} {c.id}',
                )],
                await category_repository.get_categories(group_id=group_id),
            ))
            await self.send_message(
                strings.choose_variant,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

    async def send_schedule_timings(self, args: list[Any], callback_id: ButtonCallback):
        if len(args) < 1:
            await self.send_message(text=strings.choose_variant)
        else:
            category_id = args[0]
            keyboard = list(map(
                lambda item: [InlineKeyboardButton(
                    f'{item}',
                    callback_data=f'{callback_id.value} {category_id} {item}',
                )],
                range(1, 11)
            ))
            await self.send_message(
                strings.choose_frequency,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

    async def send_schedule_quiz(self, args: list[Any]):
        if len(args) < 2 or not args[1].isdigit():
            await self.send_message(text=strings.choose_frequency)
        else:
            category_id = str(args[0])
            frequency = int(args[1])
            self.user.scheduled_category_id = category_id
            self.user.scheduled_frequency = frequency
            await self.send_message(strings.scheduled_succ)
            await self.send_main_menu()

    async def send_schedule_cancel(self):
        self.user.scheduled_category_id = ''
        self.user.scheduled_frequency = 0
        await self.send_message(strings.schedule_cancel)
        await self.send_main_menu()
