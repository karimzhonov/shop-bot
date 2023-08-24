
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline.categories import categories_markup, category_cb
from bot.keyboards.inline.products_from_catalog import product_markup, product_cb
from aiogram.utils.callback_data import CallbackData
from aiogram.types.chat import ChatActions
from bot.loader import dp, bot
from .menu import catalog
from bot.filters import IsUser
from product.models import Category, Product
from order.models import Cart
from bot.utils import get_file_path


@dp.message_handler(IsUser(), text=catalog)
async def process_catalog(message: Message):
    await message.answer('Выберите раздел, чтобы вывести список товаров:',
                         reply_markup=await categories_markup(None))


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict):
    childred_categories = Category.objects.filter(parent_id=callback_data.get("id"))

    if await childred_categories.aexists():
        await query.message.edit_reply_markup(await categories_markup(callback_data.get("id")))
    else:
        products = Product.objects.filter(
            category_id=callback_data.get("id"),
        )
        await query.answer('Все доступные товары.')
        await show_products(query.message, products)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: CallbackQuery, callback_data: dict):
    cart, created = await Cart.objects.aget_or_create(user_id=query.from_user.id, product_id=callback_data.get("id"))
    if not created:
        await Cart.objects.filter(id=cart.id).aupdate(qty=cart.qty + 1)
    await query.answer('Товар добавлен в корзину!')


async def show_products(m, products):

    if not await products.aexists():

        await m.answer('Здесь ничего нет 😢')

    else:

        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

        async for product in products:

            markup = product_markup(product.id, product.price)
            text = f'<b>{product.name}</b>\n\n{product.desc}'

            await m.answer_photo(photo=open(get_file_path(product.photo), "rb"),
                                 caption=text,
                                 reply_markup=markup)
