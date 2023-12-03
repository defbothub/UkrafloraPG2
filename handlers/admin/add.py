
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ContentType, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData
from keyboards.default.markups import *
from states import ProductState, CategoryState
from aiogram.types.chat import ChatActions
from handlers.user.menu import settings
from loader import dp, db, bot, logger
from utils.db.models import Сategories, Products
from filters import IsAdmin
import ast


category_cb = CallbackData('category', 'id', 'action')
product_cb = CallbackData('product', 'id', 'action')

add_product = '➕ Додати товар'
delete_category = '🗑️ Видалити категорію'

# Нажатие на "⚙ Налаштування"
@dp.message_handler(IsAdmin(), text=settings)
async def process_settings(message: Message):

    markup = InlineKeyboardMarkup()
    result = db.db_session.query(Сategories).all()
    for categorie in result:
        markup.add(InlineKeyboardButton(
            categorie.title, callback_data=category_cb.new(id=categorie.id, action='view')))

    markup.add(InlineKeyboardButton(
        '+ Додати категорію', callback_data='add_category'))

    await message.answer('Налаштування категорій:', reply_markup=markup)


# Просмотреть категорию
@dp.callback_query_handler(IsAdmin(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):

    category_id = callback_data['id']
    # Получить все товары из категории
    products = db.db_session.query(Products).\
        filter(Products.categori_id == category_id).\
        all()
    await query.message.delete()
    await query.answer('Всі додані товари в цю категорію.')
    await state.update_data(category_index=category_id)
    await show_products(query.message, products)


# Добавить категорию
@dp.callback_query_handler(IsAdmin(), text='add_category')
async def add_category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    await query.message.answer('Яка назва категорії?', reply_markup=menu_markup())
    await CategoryState.title.set()

# Ввести имя категории
@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: Message, state: FSMContext):
    category = message.text
    logger.info(
        f"Admin id - {message.from_user.id} name - {message.from_user.first_name} add category {category}")
    db.db_session.add(Сategories(title=category))
    db.db_session.commit()
    await state.finish()
    await process_settings(message)

# Удалить категорию
@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: Message, state: FSMContext):

    async with state.proxy() as data:
        if 'category_index' in data.keys():
            logger.info(
                f"Admin id - {message.from_user.id} name - {message.from_user.first_name} add category {message.text}")
            idx = int(data['category_index'])
            # Берем категорию по id
            category = db.db_session.query(Сategories).filter_by(id=idx).first()
            db.db_session.delete(category)
            db.db_session.commit()
            await message.answer('Готово!', reply_markup=menu_markup())
            await process_settings(message)


# Добавить продукт в категорию
@dp.message_handler(IsAdmin(), text=add_product)
async def process_add_product(message: Message):
    await ProductState.title.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)
    await message.answer('Яка назва?', reply_markup=markup)


# Нажал на ОТМЕНИТЬ при вводе название товара
@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Ок, відмінено!', reply_markup=menu_markup())
    await state.finish()
    await process_settings(message)


# Нажал на ОТМЕНИТЬ при вводе название товара
@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.title)
async def process_title_back(message: Message, state: FSMContext):
    await process_add_product(message)


# Ввсел описание товара
@dp.message_handler(IsAdmin(), state=ProductState.title)
async def process_title(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['title'] = message.text
        data['additives'] = {}
        data['additive_queue'] = []

    await ProductState.next()
    await message.answer('Який опис?', reply_markup=back_markup())


# Нажал на ОТМЕНИТЬ при вводе описания товара -> переход на имя товара
@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.body)
async def process_body_back(message: Message, state: FSMContext):

    await ProductState.title.set()

    async with state.proxy() as data:

        await message.answer(f"Змінити назву з <b>{data['title']}</b>?", reply_markup=back_markup())


# Загрузка фотки 
@dp.message_handler(IsAdmin(), state=ProductState.body)
async def process_body(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['body'] = message.text

    await ProductState.next()
    await message.answer('Яке фото?', reply_markup=back_markup())


# Загрузка фотки 
@dp.message_handler(IsAdmin(), content_types=ContentType.PHOTO, state=ProductState.image)
async def process_image_photo(message: Message, state: FSMContext):

    fileID = message.photo[-1].file_id
    file_info = await bot.get_file(fileID)
    downloaded_file = (await bot.download_file(file_info.file_path)).read()

    async with state.proxy() as data:
        data['image'] = downloaded_file

    await ProductState.next()
    await message.answer('Яка ціна?', reply_markup=back_markup())


# Если прислал не фотку 
@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT, state=ProductState.image)
async def process_image_url(message: Message, state: FSMContext):
    if message.text == back_message:
        await ProductState.body.set()
        async with state.proxy() as data:
            await message.answer(f"Змінити опис з <b>{data['body']}</b>?", reply_markup=back_markup())
    else:
        await message.answer('Потрібно прислати фото товару.')


# Если прислал не фотку -> просим указать число
@dp.message_handler(IsAdmin(), lambda message: not message.text.isdigit(), state=ProductState.price)
async def process_price_invalid(message: Message, state: FSMContext):
    if message.text == back_message:
        await ProductState.image.set()
        async with state.proxy() as data:
            await message.answer("Замінити зображення на інше?", reply_markup=back_markup())
    else:
        await message.answer('Вкажіть ціну у вигляді числа!')


# Проверка на число 
@dp.message_handler(IsAdmin(), lambda message: message.text.isdigit(), state=ProductState.price)
async def process_price(message: Message, state: FSMContext):
    async with state.proxy() as data:

        title = data['title']
        body = data['body']
        data['price'] = message.text
        price = data['price']

        await ProductState.confirm.set()
        text = f'<b>{title}</b>\n\n{body}\n\nЦіна: {price} ₴'

        markup = check_markup()

        await message.answer_photo(photo=data['image'],
                                   caption=text,
                                   reply_markup=markup)


# Проверка введеное ли верно поле 
@dp.message_handler(IsAdmin(), lambda message: message.text not in [back_message, all_right_message], state=ProductState.confirm)
async def process_confirm_invalid(message: Message):
    await message.answer('Такого варіанту не було.')


# При потверждении нажатие НАЗАД 
@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: Message, state: FSMContext):
    await ProductState.price.set()
    async with state.proxy() as data:
        now_additive = data["additive_queue"][-1]
        await ProductState.additive_price.set()
        await message.answer(f"{now_additive} Змінити ціну з <b>{data['additives'][now_additive]}</b>?", reply_markup=back_markup())


# При потверждении нажатие ПОТВЕРДИТЬ и добавить в базу 
@dp.message_handler(IsAdmin(), text=all_right_message, state=ProductState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    async with state.proxy() as data:

        title = data['title']
        body = data['body']
        image = data['image']
        price = data['price']
        category_id = data['category_index']

        logger.info(
            f"Admin id - {message.from_user.id} name - {message.from_user.first_name} add product {title} into {data['category_index']}")
        produtc = Products(categori_id=category_id, title=title,
                           body=body, photo=image, price=price)
        db.db_session.add(produtc)
        db.db_session.commit()

    await state.finish()
    await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
    await process_settings(message)


# Удалить продукт
@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery, callback_data: dict):
    product_idx = callback_data['id']
    logger.info(
        f"Admin id - {query.from_user.id} name - {query.from_user.first_name} delete product with index - {product_idx}")
    product = db.db_session.query(Products).filter_by(id=product_idx).first()
    db.db_session.delete(product)
    db.db_session.commit()
    await query.answer('Видалено!')
    await query.message.delete()

# Показать продукты
async def show_products(m, products):
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
    for product in products:
        text = f'<b>{product.title}</b>\n\n{product.body}\n\n'

        text += f"\nЦіна: {product.price} ₴"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            '🗑️ Видалити', callback_data=product_cb.new(id=product.id, action='delete')))
        await m.answer_photo(photo=product.photo,
                             caption=text,
                             reply_markup=markup)

    markup = ReplyKeyboardMarkup()
    markup.add(add_product)
    markup.add(delete_category)
    markup.add(menu_message)

    await m.answer('Хочете щось додати чи видалити?', reply_markup=markup)
