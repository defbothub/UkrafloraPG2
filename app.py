from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.user.menu import cart, catalog, contacts, sale
import os
import handlers
from keyboards import *
from aiogram import executor, types
from data import config
from utils.db.db_loader import DATABASE_URL    #додав для статистики
import psycopg2 as ps                          # додав для статистики
from loader import dp, db, bot
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
    if message.from_user.id in config.ADMINS:

        #config.ADMINS.append(cid)
        await message.answer('Вітаю тебе Адміне!'
                             '\nГарного робочого дня 🤗'
                             '\nТисни Menu і почнемо...', reply_markup=menu_markup())
        return
    else:

        base = ps.connect(DATABASE_URL, sslmode='require')
        cur = base.cursor()
        user_id = message.from_user.id
        cur.execute("SELECT * FROM users_ukrflr WHERE id = %s;", (user_id,))
        data = cur.fetchone()
        print(data)

        if data is None:
            try:
                print("ok")
                cur.execute("INSERT INTO users_ukrflr (id, active) VALUES (%s, %s);", (user_id, 1))
                print("ok1")
                base.commit()
                cur.close()
                await message.answer('''Натисніть Menu, щоб продовжити.   👇''',
                                     reply_markup=menu_markup())
            except Exception as e:
                print("Помилка при виконанні SQL-запиту:", e)

        else:
            await message.answer('''Натисніть Menu, щоб продовжити   👇''',
                             reply_markup=menu_markup())


@dp.message_handler(commands='select')
async def count_users(message: types.Message):
    if message.chat.type == 'private':
        base = ps.connect(DATABASE_URL, sslmode='require')
        cur = base.cursor()
        cur.execute("SELECT COUNT(*) as users_amount FROM users_ukrflr ")
        data = cur.fetchone()[0]
        cur.close()
        base.close()
        await message.answer(f"Украфлора має {data} користувачів 👫")

@dp.message_handler(commands='sendall')
async def sendall(message: types.Message):
    if message.chat.type == 'private':
        try:
            base = ps.connect(DATABASE_URL, sslmode='require')
            cur = base.cursor()
            cur.execute("SELECT id, active FROM users_ukrflr")
            users = cur.fetchall()
            text = message.text[9:]
            for row in users:
                try:
                    await bot.send_message(row[0], text)
                    if int(row[1]) != 1:
                        user_id = row[0]
                        active = 1
                        cur.execute("UPDATE users_ukrflr SET active = %s WHERE id = %s;", (active, user_id))

                except Exception as e:
                    print(f"Error sending message to user {row[0]}: {e}")
                    user_id = row[0]
                    active = 0
                    cur.execute("UPDATE users_ukrflr SET active = %s WHERE id = %s;", (active, user_id))

            base.commit()
        except Exception as e:
            print(f"Помилка з'єднання з базою даних: {e}")
        finally:
            cur.close()
            base.close()
        await bot.send_message(message.from_user.id, "Повідомлення розіслано!")



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
