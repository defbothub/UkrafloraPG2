from aiogram.types import ContentType, Message
from keyboards.default.markups import *
from handlers.user.menu import sale_setting
from loader import dp, db, bot
from utils.db.models import Promotion
from filters import IsAdmin
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers.user.menu import markup_admin

class PromotionState(StatesGroup):
    add_promotion_description = State()  # Додавання опису акції
    add_promotion_photo = State()  # Додавання фото акції


add_sale = '➕ Додати акцію'
delete_sale = '🗑️ Видалити акцію'
back_sale = '👈 в головне меню'

# зберігання опису та фото акції в базі даних
def save_promotion_to_database(caption, photo_data):
    try:
        promotion = Promotion(caption=caption, photo=photo_data)
        db.db_session.add(promotion)
        db.db_session.commit()
        print("Promotion saved to the database successfully.")
    except Exception as e:
        print(f"Error saving promotion to the database: {e}")
        db.db_session.rollback()

# Нажатие на "🔥 Налаштування акції"
@dp.message_handler(IsAdmin(), text=sale_setting)
async def process_settings(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(add_sale)
    markup.add(delete_sale)
    markup.add(back_sale)
    await message.answer('Перед додаванням нової акції видаліть попередню.', reply_markup=markup)

# Нажатие на "➕ Додати акцію"
@dp.message_handler(IsAdmin(), text=add_sale)
async def add_promotion_handler(message: Message, state: FSMContext):
    await message.answer('Введіть опис акції:')
    await PromotionState.add_promotion_description.set()

# Введення опису акції
@dp.message_handler(IsAdmin(), state=PromotionState.add_promotion_description)
async def add_promotion_description_handler(message: Message, state: FSMContext):
    caption = message.text
    async with state.proxy() as data:
        data['description'] = caption
    await message.answer('Будь ласка, надішліть фото акції:')
    await PromotionState.next()

@dp.message_handler(IsAdmin(), content_types=ContentType.PHOTO, state=PromotionState.add_promotion_photo)
async def add_promotion_photo_handler(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    photo_data = (await bot.download_file(file_info.file_path)).read()
    async with state.proxy() as data:
        caption = data['description']

    save_promotion_to_database(caption, photo_data)

    await state.finish()
    await message.answer('Акцію додано!', reply_markup=markup_admin)

#  "🗑️ Видалити акцію"
@dp.message_handler(IsAdmin(), text=delete_sale)
async def delete_promotion_handler(message: Message):
    # Очистити таблицю promotions
    db.db_session.query(Promotion).delete()
    db.db_session.commit()
    await message.answer('Таблицю акцій очищено!\nТепер можна додати нову акцію.')

#  в головне меню
@dp.message_handler(IsAdmin(), text=back_sale)
async def to_admin_menu(message: Message):
    await message.answer('Головне меню.', reply_markup=markup_admin)
