from aiogram.fsm.state import State, StatesGroup

class Admin(StatesGroup):
    user_id = State()
    make_active = State()