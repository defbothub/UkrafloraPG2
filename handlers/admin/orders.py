
from aiogram.types import Message
from utils.db.models import Products, Ordered_products, Orders
from loader import dp, db, logger
from handlers.user.menu import orders
from filters import IsAdmin

#Показать заказы
@dp.message_handler(IsAdmin(), text=orders)
async def process_orders(message: Message):
    logger.info(
        f"Admin id - {message.from_user.id} name - {message.from_user.first_name} view orders")
    orders = db.db_session.query(Orders).filter_by(is_orderd=True).all()
    if len(orders) == 0:
        await message.answer('Немає нових замовлень.')
    else:
        await order_answer(message, orders)


async def order_answer(message, orders):
    res = ''
    st = 0
    for order in orders:
        st += 1
        products = db.db_session.query(
            Ordered_products).filter_by(order_id=order.id).all()
        res += f"<b>Замовлення</b> N{order.id} \n<b>Від:</b> {order.usr_name}\n<b>На адресу:</b> {order.usr_address}\n"
        for ordered_product in products:
            product = db.db_session.query(Products).filter_by(
                id=ordered_product.product_id).first()
            if product == None:
                name = "Товару немає в базі"
            else:
                name = product.title
            num = ordered_product.quantity
            res += f'{name}, в кількості-{num} шт.'
        res += "\n\n"

    await message.answer(res)
