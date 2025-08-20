from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.users.dao import UsersDAO
from app.database.referrals.dao import ReferralsDAO
from app.config import settings
from app.callbacks.admin.callback import *

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

admin_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="admin_back")]
])

admin_info_about_user = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Информация о пользователе", callback_data="user_info")]
]) 

user_info = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отвязать активную реферальную ссылку", callback_data="unbind_link")],
        [InlineKeyboardButton(text="Все рефералки пользователя", callback_data="all_ref_links")],
        [InlineKeyboardButton(text="Удалить полностью", callback_data="delete_user")],
    ])


confirm_delete_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="confirm_delete_yes"),
            InlineKeyboardButton(text="Нет", callback_data="confirm_delete_no"),
        ]
    ]
)