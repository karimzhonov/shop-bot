
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery, Message
from bot.models import User


class IsAdmin(BoundFilter):

    async def check(self, message: Message):
        message = message.message if isinstance(message, CallbackQuery) else message
        return await User.objects.filter(id=message.chat.id, is_admin=True).aexists()
