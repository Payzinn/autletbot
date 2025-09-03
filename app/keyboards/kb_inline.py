from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.users.dao import UsersDAO
from app.database.referrals.dao import ReferralsDAO
from app.config import settings

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💵 Регистрация/ознакомительный доступ", callback_data="buy_abonement")],
    # [InlineKeyboardButton(text="🍀 Получить пробный 7-и дневный период", callback_data="get_seven_days_trial")],
    [InlineKeyboardButton(text="📜 Получить пригласительную ссылку", callback_data="give_invite_link")],
])

check_subscription = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить", callback_data="check_sub")]
])

async def abonement_keyboard(link: str, button_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, url=link)],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="back")]
])

admin_main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Управление пользователями", callback_data="user_info")],
])

users_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Инфо о пользователе", callback_data="user_info")],
    [InlineKeyboardButton(text="Назад", callback_data="back_to_main")],
])

user_info_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отвязать рефералку", callback_data="unbind_link")],
    [InlineKeyboardButton(text="Все реферальные ссылки", callback_data="all_ref_links")],
    [InlineKeyboardButton(text="Удалить пользователя", callback_data="delete_user")],
    [InlineKeyboardButton(text="Сделать админом", callback_data="make_admin")],
    [InlineKeyboardButton(text="Отозвать админ", callback_data="cancel_admin")],
    [InlineKeyboardButton(text="Назад", callback_data="back_to_users")],
])

confirm_delete_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да", callback_data="confirm_delete_yes"),
     InlineKeyboardButton(text="Нет", callback_data="confirm_delete_no")],
])

admin_back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="back_to_user_info")],
])