import datetime

from address.models import Address
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bot.keyboards.datepicker import Datepicker, DatepickerSettings
from bot.keyboards.inline_timepicker.inline_timepicker import InlineTimepicker
from order.models import ORDER_DELIVERY_TYPE, PAYMENT_TYPES
from django.utils import timezone
back_message = '👈 Назад'
confirm_message = '✅ Подтвердить заказ'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'

def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(cancel_message)

    return markup

def back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup

def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)

    return markup

def submit_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)

    return markup


def dtype_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for key, value in ORDER_DELIVERY_TYPE:
        markup.row(value)

    return markup

def ptype_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for key, value in PAYMENT_TYPES:
        markup.row(value)

    return markup

async def address_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    async for address in Address.objects.all():
        markup.row(address.name)
    return markup


def send_my_location_markup():
    keyboard = ReplyKeyboardMarkup()
    button = KeyboardButton("Отправить геопозиции", request_location=True)
    keyboard.add(button)
    return keyboard

def datepicker_settings():
    return DatepickerSettings(
        # views={
        #     'day': {
        #         'footer': ['prev-month', 'today', 'next-month'],
        #     },
        #     'month': {
        #         'footer': ['today']
        #     },
        #     'year': {
        #         'header': ['today'],
        #     }
        # },
        # custom_actions=[TodayAction]
    )

def datepicker_markup():
    datepicker = Datepicker(datepicker_settings())
    return datepicker.start_calendar()

inline_timepicker = InlineTimepicker()

def timepicker_markup():
    now = datetime.datetime.now()
    inline_timepicker.init(
        datetime.time(now.hour, now.minute),
        datetime.time(1),
        datetime.time(23),
        minute_step=5,
    )
    return inline_timepicker.get_keyboard()