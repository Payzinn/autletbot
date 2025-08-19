from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.users.dao import UsersDAO
from app.config import settings

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💵 Приобрести абонемент", callback_data="buy_abonement")],
    [InlineKeyboardButton(text="🍀 Получить пробный 7-и дневный период", callback_data="get_seven_days_trial")],
    [InlineKeyboardButton(text="📜 Выдать пригласительную ссылку", callback_data="give_invite_link")],
])

async def abonement_keyboard(link: str, button_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, url=link)],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="back")]
])