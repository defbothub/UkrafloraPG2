from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from utils.db.models import Сategories, Products
from loader import db

category_cb = CallbackData('category', 'id', 'action')


def categories_markup():
    global category_cb
    
    markup = InlineKeyboardMarkup()
    for category in db.db_session.query(Сategories).all():
        markup.add(InlineKeyboardButton(category.title, callback_data=category_cb.new(id=category.id, action='view')))

    return markup
