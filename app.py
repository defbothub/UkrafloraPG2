from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.user.menu import cart, catalog, contacts, sale
import os
import handlers
from keyboards import *
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from data import config
from loader import dp, db, bot
import filters
import logging
import aioschedule
import asyncio
import datetime
import psycopg2 as ps
from utils.db.db_loader import DATABASE_URL


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

        base = ps.connect(DATABASE_URL, sslmode='require')
        cur = base.cursor()
        user_id = message.from_user.id
        cur.execute("SELECT * FROM users_uf WHERE id = %s;", (user_id,))
        data = cur.fetchone()

        if data is None:
            cur.execute("INSERT INTO users_uf (id) VALUES (%s);", (user_id,))
            base.commit()
            cur.close()
            await message.answer('''Натисніть Menu, щоб продовжити.   👇''',
                             reply_markup=menu_markup())
        else:
            await message.answer('''Натисніть Menu, щоб продовжити.   👇''',
                             reply_markup=menu_markup())


@dp.message_handler(commands='select')
async def count_users(message: types.Message):
    if message.chat.type == 'private':
        base = ps.connect(DATABASE_URL, sslmode='require')
        cur = base.cursor()
        cur.execute("SELECT COUNT(*) as users_amount FROM users_uf ")
        data = cur.fetchone()[0]
        cur.close()
        base.close()
        await message.answer(f"Украфлора має {data} користувачів 👫")


# розсилка повідомлень


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
