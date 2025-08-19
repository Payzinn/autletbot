from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, IS_MEMBER
from aiogram import Bot
from app.config import settings
from app.keyboards.kb_inline import main, abonement_keyboard
from app.database.users.dao import UsersDAO 
from app.database.invites.dao import InvitesDAO
from app.database.subscriptions.dao import SubscriptionsDAO
from app.database.invites.states import ReferralForm
from app.database.subscriptions.models import SubscriptionType
from datetime import datetime
from datetime import timedelta
from aiogram.types import ChatMemberUpdated
import qrcode
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
bot = Bot(token=settings.BOT_TOKEN)
router = Router()

@router.message(CommandStart())
async def start(message: Message):
    tg_id = message.from_user.id
    user = await UsersDAO.find_one_or_none(tg_id=int(tg_id))
    if user is None:
        user = await UsersDAO.add_user(username = message.from_user.username, 
                                       tg_id=tg_id)
    user_channel_status = await bot.get_chat_member(chat_id=settings.CHAT_ID, 
                                                    user_id = message.from_user.id)
    if user_channel_status.status != "left":
        await message.answer("Выберите необходимое действие", reply_markup=main)
    else:
        await message.answer("Для получения пробного периода Вам необходимо подписаться на группу https://t.me/autlettravelbiznes")

@router.callback_query(F.data == "buy_abonement")
async def buy_abonement(callback: CallbackQuery):
    user = await UsersDAO.find_one_or_none(tg_id=int(callback.from_user.id))
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы", show_alert=True)
        return

    if user.referral_link:
        await callback.message.answer("У вас уже есть абонемент")
        return

    referral_url = None
    if user.invited_by:
        ref_owner = await UsersDAO.find_one_or_none(username=user.invited_by)
        if ref_owner and ref_owner.referral_link:
            referral_url = ref_owner.referral_link

    final_link = referral_url or settings.DEFAULT_REF_LINK

    await SubscriptionsDAO.add_subscription(
        user_id=user.id,
        type_sub=SubscriptionType.BASE,
        referral_link_used=final_link,
        expires_at=None
    )

    await callback.message.answer(
        "Ссылка для приобретения абонемента:",
        reply_markup=await abonement_keyboard(user.id)  
    )
    
@router.callback_query(F.data == "get_seven_days_trial")
async def get_trial(callback: CallbackQuery):
    user = await UsersDAO.find_one_or_none(tg_id=callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы", show_alert=True)
        return

    if user.referral_link:
        await callback.message.answer("У вас уже есть абонемент")
        return

    referral_url = None
    if user.invited_by:
        ref_owner = await UsersDAO.find_one_or_none(username=user.invited_by)
        if ref_owner and ref_owner.referral_link:
            referral_url = ref_owner.referral_link

    final_link = (referral_url or settings.DEFAULT_REF_LINK) + "&promo"

    expires_at = datetime.now() + timedelta(days=7)  
    await SubscriptionsDAO.add_subscription(
        user_id=user.id,
        type_sub=SubscriptionType.TRIAL,
        referral_link_used=final_link,
        expires_at=expires_at
    )

    await callback.message.answer(f"Ваша ссылка для пробного доступа: {final_link}")

@router.callback_query(F.data == "give_invite_link")
async def give_invite_link(callback: CallbackQuery, state: FSMContext):
    user = await UsersDAO.find_one_or_none(tg_id=callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы", show_alert=True)
        return

    if not user.referral_link:
        await callback.message.answer(
            "Скопируйте и вставьте Вашу реферальную ссылку в поле ниже"
        )
        await state.set_state(ReferralForm.waiting_for_ref_link)
        return

    invite = await bot.create_chat_invite_link(
        chat_id=settings.CHAT_ID,
        name=user.username,
        creates_join_request=False
    )

    qr_path = f"qrcodes/{user.tg_id}.png"
    os.makedirs("qrcodes", exist_ok=True)
    img = qrcode.make(invite.invite_link)
    img.save(qr_path)
    
    await UsersDAO.update(user.id, invite_link=invite.invite_link)
    await InvitesDAO.add_invite(owner_id=user.id, invite_link=invite.invite_link, qr_code_path=qr_path)
    input_file = FSInputFile(qr_path)

    await callback.message.answer_photo(
        photo=input_file,
        caption=f"Ваша пригласительная ссылка: {invite.invite_link}"
    )

async def save_ref_link(message: Message, state: FSMContext):
    ref_link = message.text.strip()
    print(f"ref_link: {ref_link}, type: {type(ref_link)}")
    user = await UsersDAO.find_one_or_none(tg_id=int(message.from_user.id))
    if not user:
        await message.answer("Ошибка: вы не зарегистрированы")
        await state.clear()
        return
    print(f"user.id: {user.id}, type: {type(user.id)}")
    if not isinstance(user.id, int):
        await message.answer(f"Ошибка: user.id не число, а {type(user.id)}: {user.id}")
        await state.clear()
        return
    await UsersDAO.update(user.id, referral_link=ref_link)
    user = await UsersDAO.find_one_or_none(id=user.id)
    print(f"После update, user.id: {user.id}, type: {type(user.id)}")
    await process_invite(message, user)
    await state.clear()
    
async def process_invite(event, user):
    if not isinstance(user.id, int):
        msg = f"Ошибка: user.id не число, а {type(user.id)}: {user.id}"
        if isinstance(event, CallbackQuery):
            await event.message.answer(msg)
        else:
            await event.answer(msg)
        return

    invite = await bot.create_chat_invite_link(
        chat_id=settings.CHAT_ID,
        name=user.username,
        creates_join_request=False
    )

    qr_path = f"qrcodes/{user.tg_id}.png"
    os.makedirs(BASE_DIR / "qrcodes", exist_ok=True)
    img = qrcode.make(invite.invite_link)
    img.save(BASE_DIR / qr_path)

    await UsersDAO.update(user.id, invite_link=invite.invite_link)
    await InvitesDAO.add_invite(owner_id=user.id, invite_link=invite.invite_link, qr_code_path=str(qr_path))

    await send_qr_code(event, qr_path, invite.invite_link)

@router.chat_member()
async def track_invites(event: ChatMemberUpdated):
    if event.new_chat_member.status != "member":
        return

    if not event.invite_link:
        return

    invite = await InvitesDAO.find_by_link(event.invite_link.invite_link)
    if not invite:
        return

    ref_owner = await UsersDAO.find_by_id(invite.owner_id)
    if not ref_owner:
        return

    user = await UsersDAO.find_one_or_none(tg_id=event.from_user.id)
    if user:
        await UsersDAO.update(user.id, invited_by=ref_owner.username)


async def send_qr_code(event, qr_path, invite_link):
    full_path = BASE_DIR / qr_path
    input_file = FSInputFile(full_path)
    caption = f"Ваша пригласительная ссылка: {invite_link}"

    if isinstance(event, CallbackQuery):
        await event.message.answer_photo(input_file, caption=caption)
    else:
        await event.answer_photo(input_file, caption=caption)