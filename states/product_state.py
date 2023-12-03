from aiogram.dispatcher.filters.state import StatesGroup, State

class ProductState(StatesGroup):
    title = State()
    body = State()
    image = State()
    price = State()
    # additive = State()
    # additive_price = State()
    confirm = State()

class CategoryState(StatesGroup):
    title = State()