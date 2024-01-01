import enum
from typing import Coroutine, Callable, Any

from telegram import Update


class ButtonCallback(enum.Enum):
    QUIZ = 'quiz'
    CATEGORIES = 'categories'
    CATEGORY_GROUP = 'category_group'
    SCHEDULE_CATEGORIES = 'schedule_categories'
    SCHEDULE_CATEGORY_GROUP = 'schedule_category_group'
    SCHEDULE_CATEGORY_TIMINGS = 'schedule_category_timings'
    SCHEDULE_QUIZ = 'schedule_quiz'
    SCHEDULE_CANCEL = 'schedule_cancel'


class ButtonHandler:
    handlers = dict[ButtonCallback, Callable[[list[Any]], Coroutine]]()

    def add_handler(self, callback_id: ButtonCallback, handler: Callable[[list[Any]], Coroutine]):
        self.handlers[callback_id] = handler

    async def handle(self, update: Update):
        query = update.callback_query
        if query and query.data:
            tokens = query.data.split()
            if len(tokens) > 0:
                args = tokens[1:]
                for callback_id, handler in self.handlers.items():
                    if tokens[0] == callback_id.value:
                        await handler(args)
