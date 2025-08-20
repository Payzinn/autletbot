from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Bot
from app.config import settings
from app.keyboards.kb_inline import admin_info_about_user, user_info, confirm_delete_kb
from app.database.users.dao import UsersDAO 
from app.database.referrals.dao import ReferralsDAO 
from app.database.invites.dao import InvitesDAO
from app.database.referrals.models import ReferralStatus
from app.database.users.states import Admin
from datetime import datetime
from datetime import timedelta
from aiogram.types import ChatMemberUpdated
import qrcode
import os
from pathlib import Path
from app.callbacks.admin.callback import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent
bot = Bot(token=settings.BOT_TOKEN)
router = Router()

@router.message(Command('admin'))
async def start_admin_cmd(message: Message, state: FSMContext):
    if int(message.from_user.id) == settings.ADMIN_ID:
        await state.clear()
        await message.answer("Админ меню", reply_markup=admin_info_about_user)

@router.callback_query(F.data == "user_info")
async def user_info_input(callback: CallbackQuery, state: FSMContext):
    if int(callback.from_user.id) == settings.ADMIN_ID:
        await state.set_state(Admin.user_id)
        await callback.message.edit_text("Введите Телеграм ID пользователя")

@router.message(Admin.user_id)
async def user_info_check(message: Message, state: FSMContext):
    if int(message.from_user.id) == settings.ADMIN_ID:
        if not message.text.isdigit():
            await message.answer("ID пользователя должно содержать только цифры!\Введите Телеграм ID пользователя ещё раз: ")
            return
        
        await state.update_data(user_id=int(message.text))
        data = await state.get_data()
        user = await UsersDAO.find_by_tg_id(int(data["user_id"]))

        if not user:
            await message.answer("Пользователь не найден в базе данных.\n Введите ID ещё раз")
            return
        await message.answer(f"Инфо о пользователе\nUsername: {user.username}\nTelegram ID: {user.tg_id}\nДата регистрации: {user.created_at}\nПригласительная ссылка: {user.invite_link or "Нет"}\nКем приглашен: {user.invited_by or "Никто"}", reply_markup=user_info)

@router.callback_query(F.data == "unbind_link")
async def user_unbind_link(callback: CallbackQuery, state: FSMContext):
    if int(callback.from_user.id) == settings.ADMIN_ID:
        data = await state.get_data()
        user = await UsersDAO.find_by_tg_id(int(data['user_id']))
        
        active_referral = await ReferralsDAO.find_by_user_id_active(user.id)
        if not active_referral:
            await callback.message.answer(f"Не удалось отвязать рефералку у пользователя [{data['user_id']}].\nСкорее всего у него все рефки уже отвязаны.")      
            return
        
        await ReferralsDAO.update_status(referral_id=active_referral.id, status=ReferralStatus.DISABLED)
        
        await callback.message.answer(f"У пользователя [{data['user_id']}] отвязалась рефералка:\n{active_referral.referral_link}") 

@router.callback_query(F.data == "all_ref_links")
async def user_all_links(callback: CallbackQuery, state: FSMContext):
    if int(callback.from_user.id) == settings.ADMIN_ID:
        data = await state.get_data()
        user = await UsersDAO.find_by_tg_id(int(data['user_id']))
        
        if not user:
            await callback.message.answer(f"Не удалось найти пользователя с ID [{data['user_id']}]")      
            return  

        referrals = await ReferralsDAO.find_by_user_id_all(user.id)

        if not referrals:
            await callback.message.answer(f"У пользователя [{user.tg_id}] нет реферальных ссылок")
            return

        text = f"Все реферальные ссылки пользователя [{user.tg_id}]:\n"
        for num,ref in enumerate(referrals):
            text += f"{num+1}. {ref.referral_link} (статус: {ref.status.value})\n"
        await state.set_state(Admin.make_active)
        await callback.message.answer(f"{text}\n\nВведите номер ссылки которая должна стать активной")

@router.message(Admin.make_active)
async def make_link_active(message: Message, state: FSMContext):
    if int(message.from_user.id) != settings.ADMIN_ID:
        return
    
    if not message.text.isdigit():
        await message.answer("Введите ещё раз именно порядковый номер ссылки, он рядом с ссылкой.")
        return

    index = int(message.text) - 1
    data = await state.get_data()
    user = await UsersDAO.find_by_tg_id(int(data['user_id']))
    referrals = await ReferralsDAO.find_by_user_id_all(user.id)

    if index < 0 or index >= len(referrals):
        await message.answer("Неверный номер ссылки, попробуйте снова.")
        return

    for i, ref in enumerate(referrals):
        status = ReferralStatus.ACTIVE if i == index else ReferralStatus.DISABLED
        await ReferralsDAO.update_status(referral_id=ref.id, status=status)

    await message.answer(f"Ссылка {referrals[index].referral_link} теперь активна!")
    await state.clear()
        
@router.callback_query(F.data == "delete_user")
async def delete_user(callback: CallbackQuery, state: FSMContext):
    if int(callback.from_user.id) != settings.ADMIN_ID:
        return
    
    data = await state.get_data()
    user_id = data.get("user_id")

    print(f"Попытка удалить пользователя с user_id={user_id} ({type(user_id)})")
    if not user_id:
        await callback.message.answer("Сначала выберите пользователя.")
        return

    await callback.message.answer(
        f"Вы уверены, что хотите удалить пользователя с ID [{user_id}]?\nЭто удалит его из всех таблиц.",
        reply_markup=confirm_delete_kb
    )

@router.callback_query(F.data == "confirm_delete_yes")
async def confirm_delete_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    user = await UsersDAO.find_by_tg_id(user_id)
    print(f"user_id: {user_id}")
    print(f"data: {data}")
    if not user_id:
        await callback.message.answer("Пользователь не выбран.")
        return
    
    await ReferralsDAO.delete_by_user_id(user.id)

    await UsersDAO.delete(user.id)

    await callback.message.answer(f"Пользователь [{user_id}] успешно удалён!")
    await state.clear()


@router.callback_query(F.data == "confirm_delete_no")
async def confirm_delete_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Удаление пользователя отменено.")
    await state.clear()