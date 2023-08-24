from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from product.models import Category

category_cb = CallbackData('category', 'id', 'action')


async def categories_markup(parent_id):

    global category_cb
    
    markup = InlineKeyboardMarkup()

    filter_kwargs = {}
    if parent_id is None:
        filter_kwargs['parent__isnull'] = True
    else:
        filter_kwargs["parent_id"] = parent_id

    async for cat in Category.objects.filter(**filter_kwargs):
        markup.add(InlineKeyboardButton(cat.name, callback_data=category_cb.new(id=cat.id, action='view')))

    return markup
