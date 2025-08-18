from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.users.dao import UsersDAO
from app.config import settings

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Приобрести абонемент", callback_data="buy_abonement")],
    [InlineKeyboardButton(text="Получить пробный 7-и дневный период", callback_data="get_seven_days_trial")],
    [InlineKeyboardButton(text="Выдать пригласительную ссылку", callback_data="give_invite_link")],
])

async def abonement_keyboard(user_id: int) -> InlineKeyboardMarkup:
    user = await UsersDAO.find_one_or_none(id=user_id)
    if not user:
        return InlineKeyboardMarkup(inline_keyboard=[])
    link = user.referral_link or settings.DEFAULT_REF_LINK
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купить абонемент", url=link)]
    ])
