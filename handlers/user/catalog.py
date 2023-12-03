
from aiogram.types import Message, CallbackQuery
from keyboards.inline.categories import categories_markup, category_cb
from keyboards.inline.products_from_catalog import product_markup, product_cb, show_products_markup
from loader import dp, db, bot, logger
from .menu import catalog
from filters import IsUser
from loader import dp, db, bot, logger
from utils.db.models import Products, Ordered_products, Orders


'''При нажатии на "Магазин" '''
@dp.message_handler(IsUser(), text=catalog)
async def process_catalog(message: Message):
    await message.answer('Оберіть розділ, щоб вивести список товарів 👇',
                         reply_markup=categories_markup())

'''При нажатии на КАТЕГОРИЮ(появляется товары) '''
@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict):
    products = db.db_session.query(Products).filter_by(
        categori_id=callback_data['id']).all()
    await bot.answer_callback_query(query.id)
    ls = []
    for product in products:
        ls.append((product.title, product.id))
    if ls == []:
        await query.message.answer('Тут нічого немає.')
    await query.message.answer('Оберіть товар зі списку 👇 ', reply_markup=show_products_markup(ls))

'''При нажатии на ТОВАР '''
@dp.callback_query_handler(IsUser(), product_cb.filter(action='view'))
async def show_products(query: CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(query.id)
    products = db.db_session.query(Products).filter_by(
        id=callback_data['id']).first()
    logger.info(
        f"User id - {query.from_user.id} name - {query.from_user.first_name} looked {products.title}")
    markup = product_markup(callback_data["id"], products.price)
    text = f'<b>{products.title}</b>\n\n{products.body} '

    await query.message.answer_photo(photo=products.photo,
                                     caption=text,
                                     reply_markup=markup)

'''При нажатии на ДОБАВИТЬ ТОВАР '''
@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: CallbackQuery, callback_data: dict):
    logger.info(
        f"User id - {query.from_user.id} name - {query.from_user.first_name} add product in cart in cart")
    if db.db_session.query(Orders).filter_by(tg_uid=query.message.chat.id).filter(Orders.is_orderd == False).count() == 0:
        order = Orders(tg_uid=query.message.chat.id, is_orderd=False)
        db.db_session.add(order)
        db.db_session.commit()
    ordered_id = db.db_session.query(Orders).filter_by(
        tg_uid=query.message.chat.id).filter(Orders.is_orderd == False).first()
    is_orderd = db.db_session.query(Ordered_products).filter(Ordered_products.order_id == ordered_id.id).filter(
        Ordered_products.product_id == callback_data['id']).count()
    if is_orderd == 0:
        ordered = Ordered_products(
            product_id=callback_data['id'], order_id=ordered_id.id, quantity=1)
        db.db_session.add(ordered)
        db.db_session.commit()

        await query.answer('Товар додано в корзину!')
        await query.message.delete()
    else:
        await query.answer('Товар вже в корзині.')
        await query.message.delete()

'''При нажатии на НАЗАД '''
@dp.callback_query_handler(IsUser(), product_cb.filter(action='delete'))
async def add_product_callback_handler(query: CallbackQuery, callback_data: dict):
    await query.message.delete()
