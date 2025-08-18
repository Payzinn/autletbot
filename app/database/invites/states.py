from aiogram.fsm.state import State, StatesGroup

class ReferralForm(StatesGroup):
    waiting_for_ref_link = State()