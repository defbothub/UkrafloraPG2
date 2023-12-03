from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.user.menu import cart, catalog, contacts, sale
import os
import handlers
from keyboards import *
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from data import config
from loader import dp, db
#, bot, base, cur
import filters
import logging
import aioschedule
import asyncio
import datetime


filters.setup(dp)

user_message = 'Користувач'
admin_message = 'Адміністратор'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    #markup = ReplyKeyboardMarkup(resize_keyboard=True)
    #markup.row(user_message, admin_message)
    cid = message.chat.id
    if cid in config.ADMINS:
        config.ADMINS.append(cid)
        await message.answer('Вітаю тебе Адміне!'
                             '\nГарного робочого дня 🤗'
                             '\nТисни Menu і почнемо...', reply_markup=menu_markup())
    else:
        await message.answer('''Натисніть Menu, щоб продовжити.   👇''',
                             reply_markup=menu_markup())

def chek_and_delete_orders():
    day_of_month = datetime.now().day
    if (day_of_month > 7 and day_of_month < 15) or day_of_month > 21:
        db.delete_orders()

async def scheduler():
    aioschedule.every().monday.at("23:19").do(chek_and_delete_orders)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)
    db.createTables()
    print("Bot online!")


async def on_shutdown():
    logging.warning("Shutting down..")
    # await bot.delete_webhook()
    # cur.close()
    # base.close()
    # await dp.storage.close()
    # await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
