from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram import Bot
from app.config import settings
from app.keyboards.kb_inline import main, abonement_keyboard, back
from app.database.users.dao import UsersDAO 
from app.database.invites.dao import InvitesDAO
from app.database.invites.states import ReferralForm
from datetime import datetime
from datetime import timedelta
from aiogram.types import ChatMemberUpdated
import qrcode
import os
from pathlib import Path