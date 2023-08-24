import logging, json
from django.utils.dateparse import parse_datetime
from django.contrib.gis.geos import Point
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.inline.products_from_cart import product_markup, product_cb
from aiogram.utils.callback_data import CallbackData
from bot.keyboards.default.markups import *
from aiogram.types.chat import ChatActions
from bot.states import CheckoutState
from bot.loader import dp, bot
from bot.filters import IsUser
from order.models import Cart, Order, ProductInOrder
from bot.utils import get_file_path
from bot.handlers.user.menu import get_menu
from bot.keyboards.datepicker import Datepicker
from .menu import cart


@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: Message, state: FSMContext):

    cart_data = Cart.objects.filter(user_id=message.chat.id).select_related('product')

    if not await cart_data.aexists():

        await message.answer('Ваша корзина пуста.' ,reply_markup=await get_menu(message))

    else:

        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data['products'] = {}

        order_cost = 0

        async for cart in cart_data:
            order_cost += cart.product.price

            async with state.proxy() as data:
                data['products'][cart.product.id] = [cart.product.name, cart.product.price, cart.qty]

            markup = product_markup(cart.product.id, cart.qty)
            text = f'<b>{cart.product.name}</b>\n\n{cart.product.desc}\n\nЦена: {cart.product.price}₽.'

            await message.answer_photo(photo=open(get_file_path(cart.product.photo), "rb"),
                                        caption=text,
                                        reply_markup=markup)

        if order_cost != 0:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('📦 Оформить заказ')

            await message.answer('Перейти к оформлению?',
                                 reply_markup=markup)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='count'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='increase'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='decrease'))
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):

    idx = str(callback_data['id'])
    action = callback_data['action']

    if 'count' == action:
        cart = await Cart.objects.aget(user_id=query.from_user.id, product_id=idx)
        await query.answer('Количество - ' + cart.qty)

    else:
        cart = await Cart.objects.aget(user_id=query.from_user.id, product_id=idx)
        count_in_cart = (cart.qty + 1) if 'increase' == action else (cart.qty - 1)

        if count_in_cart == 0:

            await Cart.objects.filter(product_id=idx, user_id=query.from_user.id).adelete()
            await query.message.delete()
            if not await Cart.objects.filter(user_id=query.from_user.id).aexists():
                await process_cart(query.message, state)
        else:
            await Cart.objects.filter(product_id=idx, user_id=query.from_user.id).aupdate(qty=count_in_cart)
            await query.message.edit_reply_markup(product_markup(idx, count_in_cart))


@dp.message_handler(IsUser(), text='📦 Оформить заказ')
async def process_checkout(message: Message, state: FSMContext):

    await CheckoutState.check_cart.set()
    await checkout(message, state)


async def checkout(message, state):
    answer = ''
    total_price = 0

    async for cart in Cart.objects.filter(user_id=message.chat.id).select_related("product"):

        tp = cart.qty * cart.product.price
        answer += f'<b>{cart.product.name}</b> * {cart.qty}шт. = {tp}₽\n'
        total_price += tp

    await message.answer(f'{answer}\nОбщая сумма заказа: {total_price}₽.',
                         reply_markup=check_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)


@dp.message_handler(IsUser(), text=all_right_message, state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await CheckoutState.dtype.set()
    await message.answer('Какой способ вам удобна',
                         reply_markup=dtype_markup())


@dp.message_handler(IsUser(), state=CheckoutState.dtype, text=dict(ORDER_DELIVERY_TYPE)['delivery'])
async def process_dtype_delivery(message: Message, state: FSMContext):
    async with state.proxy() as data:

        data["dtype"] = "delivery"
        await CheckoutState.point.set()
        await message.answer('Укажите адрес куда надо доставить',
                                 reply_markup=send_my_location_markup())


@dp.message_handler(IsUser(), state=CheckoutState.point, content_types=['location'])
async def process_point(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['point'] = [message.location.longitude, message.location.latitude]
        
        await CheckoutState.come_date.set()
        await message.answer('Укажите дата доставки', reply_markup=datepicker_markup())
        

@dp.message_handler(IsUser(), state=CheckoutState.dtype, text=dict(ORDER_DELIVERY_TYPE)["come"])
async def process_dtype_come(message: Message, state: FSMContext):
    async with state.proxy() as data:

        data["dtype"] = "come"
        await CheckoutState.address.set()
        await message.answer('Укажите один из пункт выдачи',
                                 reply_markup=await address_markup())
        
@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):
    async with state.proxy() as data:
        address = await Address.objects.aget(name=message.text)
        data["address"] = address.id
        
        await CheckoutState.come_date.set()
        await message.answer('Укажите дата доставки', reply_markup=datepicker_markup())
        
    
@dp.callback_query_handler(IsUser(), Datepicker.datepicker_callback.filter(), state=CheckoutState.come_date)
async def process_come_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    async with state.proxy() as data:
        datepicker = Datepicker(datepicker_settings())
        date = await datepicker.process(callback_query, callback_data)
        if date:
            data['come_date'] = str(date)

            await CheckoutState.come_time.set()
            await callback_query.message.answer("Укажите время доставки", 
                                                reply_markup=timepicker_markup())
        await callback_query.answer()

    
@dp.callback_query_handler(IsUser(), inline_timepicker.filter(), state=CheckoutState.come_time)
async def process_come_time(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    
    handle_result = inline_timepicker.handle(callback_query.from_user.id, callback_data)
    if handle_result is not None:
        async with state.proxy() as data:
            data['come_time'] = str(handle_result)
            await CheckoutState.ptype.set()
            await callback_query.message.answer('Укажите способ оплати',
                                reply_markup=ptype_markup())
    else:
        await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=inline_timepicker.get_keyboard())
    

@dp.message_handler(IsUser(), state=CheckoutState.ptype, text=dict(PAYMENT_TYPES)['cash'])
async def process_ptype_cash(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ptype'] = "cash"

        await confirm(message)
        await CheckoutState.confirm.set()


async def confirm(message):

    await message.answer(f'Убедитесь, что все правильно оформлено и подтвердите заказ.',
                         reply_markup=confirm_markup())


@dp.message_handler(IsUser(), text=confirm_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    enough_money = True  # enough money on the balance sheet
    markup = ReplyKeyboardRemove()

    if enough_money:

        logging.info('Deal was made.')

        async with state.proxy() as data:

            order = await Order.objects.acreate(
                user_id=message.from_user.id,
                point=Point(data.get('point', [0, 0])[0], data.get('point', [0, 0])[1]) if data.get("point", None) else None,
                dtype=data.get("dtype", None),
                address_id=data.get("address", None),
                ptype=data.get("ptype", None),
                come_date=datetime.datetime.strptime(f"{data.get('come_date')} {data.get('come_time')}", "%Y-%m-%d %H:%M:%S") 
            )

            async for cart in Cart.objects.filter(user_id=message.from_user.id).select_related('product'):
                await ProductInOrder.objects.acreate(
                    order=order,
                    product_id=cart.product_id,
                    qty=cart.qty,
                    cost=cart.qty * cart.product.price
                )
            await Cart.objects.filter(user_id=message.from_user.id).adelete()

            await message.answer('Ок! Ваш заказ уже в пути 🚀',
                                 reply_markup=markup)
    else:

        await message.answer('У вас недостаточно денег на счете. Пополните баланс!',
                             reply_markup=markup)

    await state.finish()
