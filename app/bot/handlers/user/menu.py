
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from bot.loader import dp
from bot.filters import IsAdmin, IsUser

catalog = '🛍️ Каталог'
balance = '💰 Баланс'
cart = '🛒 Корзина'
delivery_status = '🚚 Статус заказа'

settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'

@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu(message: Message):
    markup = await get_admin_keyboard()
    await message.answer('Меню', reply_markup=markup)

@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    markup = await get_user_keyboard()
    await message.answer('Меню', reply_markup=markup)


async def get_admin_keyboard():
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(settings)
    markup.add(questions, orders)
    return markup


async def get_user_keyboard():
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(balance, cart)
    markup.add(delivery_status)
    return markup


async def get_menu(message: Message):
    return await get_admin_keyboard() if await IsAdmin().check(message) else await get_user_keyboard()