from telegram import Update, InlineKeyboardMarkup

from model.user import User


class MenuStateInst:

    async def on_enter(self, user: User, update: Update):
        raise NotImplementedError()

    async def on_update(self, user: User, update: Update):
        raise NotImplementedError()

    async def send_message(
            self,
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

