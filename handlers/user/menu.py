from utils.db.models import Promotion
from loader import db

from aiogram.types import Message
from loader import dp
from keyboards import *
from filters import IsAdmin, IsUser
import asyncio

catalog = '🛍️ Магазин'
cart = '🛒 Корзина'
sale = '🎁 Акція'
contacts = '📞Контакти'

settings = '⚙ Налаштування каталогу'
orders = '🚚 Замовлення'
sale_setting = '🔥 Налаштування акції'


markup_user = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
markup_user.add(catalog, cart).add(sale, contacts)

markup_admin = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
markup_admin.add(settings).add(orders).add(sale_setting)


@dp.message_handler(IsAdmin(), text=menu_message)
async def admin_menu(message: Message):
    await message.answer('Оберіть розділ в меню.', reply_markup=markup_admin)


@dp.message_handler(IsUser(), text=menu_message)
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(catalog)
    markup.insert(cart)
    markup.add(sale).insert(contacts)
    await message.answer('Ознайомтеся з 🎁 Акцією,'
                         '\nоберіть букет в 🛍️ Магазині'
                         '\nта оформіть покупку в 🛒 Корзині.', reply_markup=markup)


@dp.message_handler(IsUser(), text=contacts)
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(catalog)
    markup.insert(cart)
    markup.add(sale).insert(contacts)
    await message.answer(' Магазини УКРАФЛОРА 🌷'
                         '\n📍 Київ, вул. Салютна, 2Б')
    await message.answer_location(latitude=50.4711362, longitude=30.4011574)
    await asyncio.sleep(2)
    await message.answer('📍 Київ, вул. Оноре де Бальзака, 2А ТЦ"Глобал"')
    await message.answer_location(latitude=50.4977949, longitude=30.5765447, reply_markup=markup)
    await message.answer('☎️ Безкоштовно по Україні')
    await message.answer("0800330088")

@dp.message_handler(IsUser(), text=sale)
async def user_menu(message: Message):
    promotion = db.db_session.query(Promotion).first()
    if promotion:
        photo_data = promotion.photo
        description = promotion.caption

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(catalog)
        markup.insert(cart)
        markup.add(sale).insert(contacts)
        await message.answer_photo(photo=photo_data, caption=description)
    else:
        await message.answer('Наразі акцій немає. Зайдіть пізніше.', reply_markup=markup_user)