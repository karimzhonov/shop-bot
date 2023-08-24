
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import BoundFilter
from bot.models import User

class IsAdmin(BoundFilter):

    async def check(self, message: Message):
        message = message.message if isinstance(message, CallbackQuery) else message
        return await User.objects.filter(id=message.chat.id, is_admin=True).aexists()
