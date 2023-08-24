from aiogram.dispatcher.filters.state import StatesGroup, State

class CheckoutState(StatesGroup):
    check_cart = State()
    dtype = State()
    point = State()
    address = State()
    ptype = State()
    come_date = State()
    come_time = State()
    confirm = State()