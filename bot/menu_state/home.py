import enum

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from model.menu_state import MenuState
from bot.menu_state.menu_state_inst import MenuStateInst
from model.user import User
from repository.repository_inst import category_repository


class ButtonCallbacks(enum.Enum):
    QUIZ = 'quiz'
    CATEGORIES = 'categories'
    CATEGORY_GROUP = 'category_group'
    SCHEDULE_CATEGORIES = 'schedule_categories'
    SCHEDULE_CATEGORY_GROUP = 'schedule_category_group'
    SCHEDULE_CATEGORY_TIMINGS = 'schedule_category_timings'
    SCHEDULE_QUIZ = 'schedule_quiz'
    SCHEDULE_CANCEL = 'schedule_cancel'


class HomeMenuState(MenuStateInst):

    async def on_enter(self, user: User, update: Update):
        await self.send_main_menu(user, update)

    async def send_main_menu(self, user: User, update: Update):
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
        await self.send_message(
            update,
            text='Выберите опцию:',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def on_update(self, user: User, update: Update):
        query = update.callback_query
        if query:
            if query.data.startswith(ButtonCallbacks.QUIZ.value):
                args = query.data.split()[1:]
                if len(args) < 1:
                    await self.send_message(update, text="Укажите категорию")
                else:
                    user.question_index = 0
                    user.menu_state = MenuState.QUIZ
                    user.quiz_category_id = args[0]

            if query.data == ButtonCallbacks.CATEGORIES.value:
                await self.send_category_groups(update, ButtonCallbacks.CATEGORY_GROUP.value)

            if query.data.startswith(ButtonCallbacks.CATEGORY_GROUP.value):
                await self.send_categories(update, ButtonCallbacks.QUIZ.value)

            if query.data == ButtonCallbacks.SCHEDULE_CATEGORIES.value:
                await self.send_category_groups(update, ButtonCallbacks.SCHEDULE_CATEGORY_GROUP.value)

            if query.data.startswith(ButtonCallbacks.SCHEDULE_CATEGORY_GROUP.value):
                await self.send_categories(update, ButtonCallbacks.SCHEDULE_CATEGORY_TIMINGS.value)

            if query.data.startswith(ButtonCallbacks.SCHEDULE_CATEGORY_TIMINGS.value):
                await self.send_schedule_timings(update, ButtonCallbacks.SCHEDULE_QUIZ.value)

            if query.data.startswith(ButtonCallbacks.SCHEDULE_QUIZ.value):
                await self.send_schedule_quiz(update, user)

            if query.data == ButtonCallbacks.SCHEDULE_CANCEL.value:
                await self.send_schedule_cancel(update, user)

    async def send_category_groups(self, update: Update, callback_name: str):
        keyboard = list(map(
            lambda c: [InlineKeyboardButton(
                c.title,
                callback_data=f'{callback_name} {c.id}',
            )],
            await category_repository.get_category_groups(),
        ))
        await self.send_message(
            update,
            "Выберите категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def send_categories(self, update: Update, callback_name: str):
        args = update.callback_query.data.split()[1:]
        if len(args) < 1:
            await self.send_message(update, text="Укажите категорию")
        else:
            group_id = args[0]
            keyboard = list(map(
                lambda c: [InlineKeyboardButton(
                    c.title,
                    callback_data=f'{callback_name} {c.id}',
                )],
                await category_repository.get_categories(group_id=group_id),
            ))
            await self.send_message(
                update,
                "Выберите вариант:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

    async def send_schedule_timings(self, update: Update, callback_name: str):
        args = update.callback_query.data.split()[1:]
        if len(args) < 1:
            await self.send_message(update, text="Укажите ID варианта")
        else:
            category_id = args[0]
            keyboard = list(map(
                lambda item: [InlineKeyboardButton(
                    f'{item}',
                    callback_data=f'{callback_name} {category_id} {item}',
                )],
                range(1, 11)
            ))
            await self.send_message(
                update,
                "Выберите число отправок в сутки:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

    async def send_schedule_quiz(self, update: Update, user: User):
        args = update.callback_query.data.split()[1:]
        if len(args) < 2 or not args[1].isdigit():
            await self.send_message(update, text="Укажите ID варианта и частоту отправки")
        else:
            category_id = args[0]
            frequency = int(args[1])
            user.scheduled_category_id = category_id
            user.scheduled_frequency = frequency
            await self.send_message(
                update,
                "Отправка запланирована"
            )
            await self.send_main_menu(user, update)

    async def send_schedule_cancel(self, update: Update, user: User):
        user.scheduled_category_id = ''
        user.scheduled_frequency = 0
        await self.send_message(
            update,
            "Отправка отменена"
        )
        await self.send_main_menu(user, update)
