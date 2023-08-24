
from aiogram.types import Message
from bot.filters import IsUser
from bot.loader import dp
from order.models import ORDER_STATUS, Order

from .menu import delivery_status


@dp.message_handler(IsUser(), text=delivery_status)
async def process_delivery_status(message: Message):
    
    orders = Order.objects.filter(user_id=message.from_user.id)
    
    if not await orders.aexists(): await message.answer('У вас нет активных заказов.')
    else: await delivery_status_answer(message, orders)

async def delivery_status_answer(message, orders):

    res = ''

    async for order in orders:

        res += f'Заказ <b>№ {order.id}</b>\n'
        
        res += f"Статус: {dict(ORDER_STATUS)[order.status]}\n"
        res += f"Сумма: {await order.acost()}\n"
        res += "Продукты:\n"
        async for pio in order.productinorder_set.select_related("product"):
            res += f'<b>{pio.product.name}</b> * {pio.qty}шт. = {pio.cost}₽\n'
        res += '\n\n'

    await message.answer(res)