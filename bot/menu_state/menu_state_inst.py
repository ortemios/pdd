from telegram import Update, InlineKeyboardMarkup

from model.user import User


class MenuStateInst:

    update: Update
    user: User

    async def on_enter(self):
        raise NotImplementedError()

    async def on_update(self):
        raise NotImplementedError()

    async def send_message(
            self,
            text: str = '',
            photo_url: str = '',
            reply_markup: InlineKeyboardMarkup = None):
        if photo_url:
            await self.update.get_bot().send_photo(
                chat_id=self.update.effective_chat.id,
                photo=photo_url
            )
        await self.update.get_bot().send_message(
            chat_id=self.update.effective_chat.id,
            text=text,
            reply_markup=reply_markup
        )

