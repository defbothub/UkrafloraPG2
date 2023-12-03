from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

product_cb = CallbackData('product', 'id', 'action')
category_temp_cb = CallbackData('view_single_product', 'action')

def show_products_markup(product_tittle):
    global product_cb

    markup = InlineKeyboardMarkup()
    for item in product_tittle:
        title, idx = item
        markup.add(InlineKeyboardButton(title, callback_data=product_cb.new(id=idx, action='view')))
    markup.add(InlineKeyboardButton(f'👈 назад', callback_data=product_cb.new(id="", action='delete')))

    return markup


def product_markup(idx='', price=0):
    global product_cb

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Додати в корзину - {price} ₴', callback_data=product_cb.new(id=idx, action='add')))
    markup.add(InlineKeyboardButton(f'👈 назад', callback_data=product_cb.new(id=idx, action='delete')))

    return markup