from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, IS_MEMBER
from aiogram import Bot
from app.config import settings
from app.keyboards.kb_inline import main, abonement_keyboard
from app.database.users.dao import UsersDAO 
from app.database.invites.dao import InvitesDAO
from app.database.invites.states import ReferralForm
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
        user = await UsersDAO.add_user(username=message.from_user.username or f"user_{tg_id}", 
                                       tg_id=tg_id)
        print(f"start: created new user id={user.id}, tg_id={tg_id}")

    user_channel_status = await bot.get_chat_member(chat_id=settings.CHAT_ID, 
                                                   user_id=message.from_user.id)
    print(f"start: user_id={tg_id}, channel_status={user_channel_status.status}")
    if user_channel_status.status != "left":
        await message.answer("Выберите необходимое действие", reply_markup=main)
    else:
        await message.answer("Для получения пробного периода Вам необходимо подписаться на группу https://t.me/autlettravelbiznes")

@router.callback_query(F.data == "buy_abonement")
async def buy_abonement(callback: CallbackQuery):
    user = await UsersDAO.find_one_or_none(tg_id=int(callback.from_user.id))
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы, пропишите /start", show_alert=True)
        return
    
    if user.referral_link:
        await callback.message.edit_text("У вас уже есть абонемент")
        return

    referral_url = None
    if user.invite_link:
        referral_url = await UsersDAO.find_referral_by_invite_link(user.invite_link)
    
    final_link = referral_url or settings.DEFAULT_REF_LINK

    # await SubscriptionsDAO.add_subscription(
    #     user_id=user.id,
    #     type_sub=SubscriptionType.BASE,
    #     referral_link_used=final_link,
    #     expires_at=None
    # )

    print(f"buy_abonement: user.id: {user.id}, type: {type(user.id)}, final_link: {final_link}")
    await callback.message.edit_text(
        "Ссылка для приобретения абонемента:",
        reply_markup=await abonement_keyboard(link=final_link, button_text="💵 Купить абонемент")
    )

@router.callback_query(F.data == "get_seven_days_trial")
async def get_trial(callback: CallbackQuery):
    user = await UsersDAO.find_one_or_none(tg_id=int(callback.from_user.id))
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы, пропишите /start", show_alert=True)
        return
    
    if user.referral_link:
        await callback.message.edit_text("У вас уже есть абонемент")
        return

    if user.referral_link:
        trial_link = f"{user.referral_link}&promo"
        await callback.message.edit_text(
            "Ваш пробный доступ:",
            reply_markup=await abonement_keyboard(link=trial_link, button_text="🍀 Получить пробный период")
        )
        return

    referral_url = None
    if user.invite_link:
        referral_url = await UsersDAO.find_referral_by_invite_link(user.invite_link)
    
    final_link = (referral_url or settings.DEFAULT_REF_LINK) + "&promo"

    # expires_at = datetime.now() + timedelta(days=7)
    # await SubscriptionsDAO.add_subscription(
    #     user_id=user.id,
    #     type_sub=SubscriptionType.TRIAL,
    #     referral_link_used=final_link,
    #     expires_at=expires_at
    # )

    await callback.message.edit_text(
        "Ваша ссылка для пробного доступа:",
        reply_markup=await abonement_keyboard(link=final_link, button_text="🍀 Получить пробный период")
    )

@router.callback_query(F.data == "give_invite_link")
async def give_invite_link(callback: CallbackQuery, state: FSMContext):
    user = await UsersDAO.find_one_or_none(tg_id=int(callback.from_user.id))
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы", show_alert=True)
        return

    if not user.referral_link:
        await callback.message.edit_text(
            "Скопируйте и вставьте Вашу реферальную ссылку в поле ниже"
        )
        await state.set_state(ReferralForm.waiting_for_ref_link)
        return

    if user.invite_link:
        invite_record = await InvitesDAO.find_one_or_none(owner_id=user.id)
        if invite_record and os.path.exists(invite_record.qr_code_path):
            input_file = FSInputFile(invite_record.qr_code_path)
            await callback.message.answer_photo(
                photo=input_file,
                caption=f"Ваша пригласительная ссылка: {user.invite_link}"
            )
            return

        qr_dir = BASE_DIR / "qrcodes"
        os.makedirs(qr_dir, exist_ok=True)
        qr_path = qr_dir / f"{user.tg_id}.png"
        img = qrcode.make(user.invite_link)
        img.save(qr_path)

        input_file = FSInputFile(qr_path)
        await callback.message.answer_photo(
            photo=input_file,
            caption=f"Ваша пригласительная ссылка: {user.invite_link}"
        )
        return

    invite = await bot.create_chat_invite_link(
        chat_id=settings.CHAT_ID,
        name=user.username,
        creates_join_request=False,
        member_limit=0  
    )
    print(f"give_invite_link: created invite_link={invite.invite_link} for user_id={user.id}")

    qr_dir = BASE_DIR / "qrcodes"
    os.makedirs(qr_dir, exist_ok=True)
    qr_path = qr_dir / f"{user.tg_id}.png"
    img = qrcode.make(invite.invite_link)
    img.save(qr_path)

    await UsersDAO.update(user.id, invite_link=invite.invite_link)
    invite_record = await InvitesDAO.add_invite(
        owner_id=user.id,
        invite_link=invite.invite_link,
        qr_code_path=str(qr_path)
    )
    print(f"give_invite_link: saved invite_record={invite_record.id if invite_record else None} for invite_link={invite.invite_link}")

    input_file = FSInputFile(qr_path)
    await callback.message.answer_photo(
        photo=input_file,
        caption=f"Ваша пригласительная ссылка: {invite.invite_link}"
    )

@router.message(ReferralForm.waiting_for_ref_link)
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
        creates_join_request=False,
        member_limit=1
    )
    print(f"process_invite: created invite_link={invite.invite_link} for user_id={user.id}")

    qr_dir = BASE_DIR / "qrcodes"
    os.makedirs(qr_dir, exist_ok=True)
    qr_path = qr_dir / f"{user.tg_id}.png"
    img = qrcode.make(invite.invite_link)
    img.save(qr_path)

    await UsersDAO.update(user.id, invite_link=invite.invite_link)
    invite_record = await InvitesDAO.add_invite(owner_id=user.id, invite_link=invite.invite_link, qr_code_path=str(qr_path))
    print(f"process_invite: saved invite_record={invite_record.id if invite_record else None} for invite_link={invite.invite_link}")

    await send_qr_code(event, qr_path, invite.invite_link)

async def send_qr_code(event, qr_path, invite_link):
    input_file = FSInputFile(qr_path)
    caption = f"Ваша пригласительная ссылка: {invite_link}"

    if isinstance(event, CallbackQuery):
        await event.message.answer_photo(input_file, caption=caption)
    else:
        await event.answer_photo(input_file, caption=caption)

@router.chat_member()
async def track_invites(event: ChatMemberUpdated):
    print(f"track_invites: user_id={event.from_user.id}, status={event.new_chat_member.status}, invite_link={getattr(event.invite_link, 'invite_link', None)}, chat_id={event.chat.id}, expected_chat_id={settings.CHAT_ID}")
    
    if event.chat.id != settings.CHAT_ID:
        print(f"track_invites: wrong chat_id={event.chat.id} (type={type(event.chat.id)}), expected={settings.CHAT_ID} (type={type(settings.CHAT_ID)})")
        return

    if event.new_chat_member.status not in ["member", "administrator", "creator"]:
        print(f"track_invites: exiting due to status={event.new_chat_member.status}")
        return

    if not event.invite_link:
        print("track_invites: no invite_link provided")
        return

    invite = await InvitesDAO.find_by_link(event.invite_link.invite_link)
    if not invite:
        print(f"track_invites: no invite found for link={event.invite_link.invite_link}")
        return

    ref_owner = await UsersDAO.find_by_id(invite.owner_id)
    if not ref_owner:
        print(f"track_invites: no ref_owner found for owner_id={invite.owner_id}")
        return

    user = await UsersDAO.find_one_or_none(tg_id=event.from_user.id)
    if not user:
        print(f"track_invites: no user found for tg_id={event.from_user.id}, creating new user")
        user = await UsersDAO.add_user(username=event.from_user.username or f"user_{event.from_user.id}", 
                                       tg_id=event.from_user.id)

    print(f"track_invites: updating user id={user.id}, tg_id={event.from_user.id} with invite_link={event.invite_link.invite_link}, invited_by={ref_owner.username}")
    await UsersDAO.update(user.id, invite_link=event.invite_link.invite_link, invited_by=ref_owner.username)

@router.message()
async def mes(message: Message):
    print(message.chat.id)