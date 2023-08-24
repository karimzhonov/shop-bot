import datetime

from address.models import Address
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bot.keyboards.datepicker import Datepicker, DatepickerSettings
from bot.keyboards.inline_timepicker.inline_timepicker import InlineTimepicker
from order.models import ORDER_DELIVERY_TYPE, PAYMENT_TYPES

back_message = '👈 Назад'
confirm_message = '✅ Подтвердить заказ'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'

def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)

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
    markup.add(back_message)
    return markup


def send_my_location_markup():
    keyboard = ReplyKeyboardMarkup()
    button = KeyboardButton("Отправить геопозиции", request_location=True)
    keyboard.add(button)
    return keyboard

def datepicker_settings():
    return DatepickerSettings()

def datepicker_markup():
    datepicker = Datepicker(datepicker_settings())
    return datepicker.start_calendar()

inline_timepicker = InlineTimepicker()

def timepicker_markup():
    
    inline_timepicker.init(
        datetime.time(12),
        datetime.time(1),
        datetime.time(23),
    )
    return inline_timepicker.get_keyboard()