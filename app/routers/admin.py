from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram import Bot
from app.config import settings
from app.keyboards.kb_inline import admin_info_about_user
from app.database.users.dao import UsersDAO 
from app.database.invites.dao import InvitesDAO
from app.database.invites.states import ReferralForm
from app.database.users.states import Admin
from datetime import datetime
from datetime import timedelta
from aiogram.types import ChatMemberUpdated
import qrcode
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
bot = Bot(token=settings.BOT_TOKEN)
router = Router()

@router.message(Command('reg'))
async def start_admin_cmd(message: Message):
    await message.answer("Админ меню", reply_markup=admin_info_about_user)

@router.callback_query(F.data == "user_info")
async def user_info_query(callback: CallbackQuery, state: FSMContext):
    state.set_state(Admin.user_id)