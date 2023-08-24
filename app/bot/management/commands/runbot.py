
import logging
import os

import bot.filters as filters
import bot.handlers as handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardRemove
from bot import config
from bot.handlers.user.menu import get_menu
from bot.loader import bot, dp
from bot.models import User
from django.core.management import BaseCommand

filters.setup(dp)

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))


@dp.message_handler(commands='start', state="*")
async def cmd_start(message: types.Message):
    await User.objects.aupdate_or_create({
        "id": message.from_user.id, 
        "username": message.from_user.username, 
        "last_name": message.from_user.last_name,
        "first_name": message.from_user.first_name,
    }, id=message.from_user.id)

    markup = await get_menu(message)

    await message.answer('''Привет! 👋

🤖 Я бот-магазин по подаже товаров любой категории.
    
🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся товары возпользуйтесь командой /menu.

❓ Возникли вопросы? Не проблема! Команда /sos поможет связаться с админами, которые постараются как можно быстрее откликнуться.

🤝 Заказать похожего бота? Свяжитесь с разработчиком <a href="https://t.me/khtkarimzhonov">Каримжонов Хусниддин</a>, он не кусается)))
    ''', reply_markup=markup)


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)

    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)
    await bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("menu", "Меню"),
        types.BotCommand("sos", "Помощь"),
    ])


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


class Command(BaseCommand):
    def handle(self, *args, **options):
        if "WEBHOOK" in list(os.environ.keys()):
    
            executor.start_webhook(
                dispatcher=dp,
                webhook_path=config.WEBHOOK_PATH,
                on_startup=on_startup,
                on_shutdown=on_shutdown,
                skip_updates=True,
                host=WEBAPP_HOST,
                port=WEBAPP_PORT,
            )

        else:

            executor.start_polling(dp, on_startup=on_startup, skip_updates=False)