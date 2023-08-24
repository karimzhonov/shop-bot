
from aiogram.types import Message
from bot.filters import IsAdmin
from bot.handlers.user.menu import orders
from bot.loader import dp


@dp.message_handler(IsAdmin(), text=orders)
async def process_orders(message: Message):
    
    orders = db.fetchall('SELECT * FROM orders')
    
    if len(orders) == 0: await message.answer('У вас нет заказов.')
    else: await order_answer(message, orders)

async def order_answer(message, orders):

    res = ''

    for order in orders:
        res += f'Заказ <b>№{order[3]}</b>\n\n'

    await message.answer(res)