from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram import Bot
from app.config import settings
from app.keyboards.kb_inline import main, abonement_keyboard, back
from app.database.users.dao import UsersDAO 
from app.database.invites.dao import InvitesDAO
from app.database.referrals.dao import ReferralsDAO
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
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await handle_start(message)

@router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    await callback.message.delete()
    await handle_start(callback.message)

async def handle_start(message: Message):
    tg_id = message.from_user.id
    user = await UsersDAO.find_by_tg_id(tg_id)
    if user is None:
        user = await UsersDAO.add_user(tg_id=tg_id, username=message.from_user.username or f"user_{tg_id}")
        print(f"start: created new user id={user.id}, tg_id={tg_id}")

    user_channel_status = await bot.get_chat_member(chat_id=settings.CHAT_ID, user_id=message.from_user.id)
    print(f"start: user_id={tg_id}, channel_status={user_channel_status.status}")

    if user_channel_status.status != "left":
        try:
            await message.edit_text("Выберите необходимое действие", reply_markup=main)
        except:
            await message.answer("Выберите необходимое действие", reply_markup=main)
    else:
        try:
            await message.edit_text(
                "Для получения пробного периода Вам необходимо подписаться на группу https://t.me/autlettravelbiznes"
            )
        except:
            await message.answer(
                "Для получения пробного периода Вам необходимо подписаться на группу https://t.me/autlettravelbiznes"
            )

@router.callback_query(F.data == "buy_abonement")
async def buy_abonement(callback: CallbackQuery):
    user = await UsersDAO.find_by_tg_id(int(callback.from_user.id))
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы, пропишите /start", show_alert=True)
        return
    
    if user.referral_id:
        referral = await ReferralsDAO.find_by_user_id(user.id)
        if referral and referral.status == "active":
            await callback.message.edit_text("У вас уже есть активный абонемент", reply_markup=back)
            return

    referral_url = None
    if user.invite_link:
        referral = await UsersDAO.find_referral_by_invite_link(user.invite_link)
        if referral:
            referral_url = referral
    
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
    user = await UsersDAO.find_by_tg_id(int(callback.from_user.id))
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы, пропишите /start", show_alert=True)
        return
    
    if user.referral_id:
        referral = await ReferralsDAO.find_by_user_id(user.id)
        if referral and referral.status == "active":
            await callback.message.edit_text("У вас уже есть активный пробный период", reply_markup=back)
            return

    referral_url = None
    if user.invite_link:
        referral = await UsersDAO.find_referral_by_invite_link(user.invite_link)
        if referral:
            referral_url = referral
    
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
    user = await UsersDAO.find_by_tg_id(int(callback.from_user.id))
    if not user:
        await callback.answer("Ошибка: вы не зарегистрированы", show_alert=True)
        return

    active_referral = await ReferralsDAO.find_by_user_id_active(user.id)
    if not active_referral:
        await callback.message.edit_text(
            "У вас нет активной реферальной ссылки.\nСкопируйте и вставьте Вашу реферальную ссылку в поле ниже:",
            reply_markup=back
        )
        await state.set_state(ReferralForm.waiting_for_ref_link)
        return

    invite_record = await InvitesDAO.find_by_owner(user.id)
    qr_dir = BASE_DIR / "qrcodes"
    os.makedirs(qr_dir, exist_ok=True)

    if invite_record:
        existing_invite = next((record for record in invite_record if os.path.exists(record.qr_code_path)), None)
        if existing_invite:
            input_file = FSInputFile(existing_invite.qr_code_path)
            caption = f"Ваша пригласительная ссылка: {existing_invite.invite_link}\n" \
                      f"Ваша активная реферальная ссылка: {active_referral.referral_link}"
            await callback.message.delete()
            await callback.message.answer_photo(photo=input_file, caption=caption, reply_markup=back)
            return

    invite = await bot.create_chat_invite_link(
        chat_id=settings.CHAT_ID,
        name=user.username,
        creates_join_request=False,
        member_limit=1
    )

    qr_path = qr_dir / f"{user.tg_id}.png"
    img = qrcode.make(invite.invite_link)
    img.save(qr_path)

    # Сохраняем invite
    await UsersDAO.update(user.id, invite_link=invite.invite_link)
    await InvitesDAO.add_invite(owner_id=user.id, invite_link=invite.invite_link, qr_code_path=str(qr_path))

    input_file = FSInputFile(qr_path)
    await callback.message.answer_photo(
        photo=input_file,
        caption=f"Ваша пригласительная ссылка: {invite.invite_link}\n"
                f"Ваша активная реферальная ссылка: {active_referral.referral_link}",
        reply_markup=back
    )

@router.message(ReferralForm.waiting_for_ref_link)
async def save_ref_link(message: Message, state: FSMContext):
    ref_link = message.text.strip()
    print(f"ref_link: {ref_link}, type: {type(ref_link)}")
    user = await UsersDAO.find_by_tg_id(int(message.from_user.id))
    if not user:
        await message.answer("Ошибка: вы не зарегистрированы")
        await state.clear()
        return
    print(f"user.id: {user.id}, type: {type(user.id)}")
    if not isinstance(user.id, int):
        await message.answer(f"Ошибка: user.id не число, а {type(user.id)}: {user.id}")
        await state.clear()
        return

    referral_id = await ReferralsDAO.add_referral(user_id=user.id, referral_link=ref_link)
    if referral_id:
        await UsersDAO.update(user.id, referral_id=referral_id)  
    else:
        await message.answer("Ошибка при создании реферальной ссылки")
        await state.clear()
        return

    user = await UsersDAO.find_by_tg_id(user.tg_id)
    print(f"После update, user.id: {user.id}, type: {type(user.id)}, referral_id: {user.referral_id}")
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
    invite_record = await InvitesDAO.add_invite(
        owner_id=user.id,
        invite_link=invite.invite_link,
        qr_code_path=str(qr_path)
    )
    print(f"process_invite: saved invite_record={invite_record.id if invite_record else None} for invite_link={invite.invite_link}")

    await send_qr_code(event, qr_path, invite.invite_link)

async def send_qr_code(event, qr_path, invite_link):
    input_file = FSInputFile(qr_path)
    caption = f"Ваша пригласительная ссылка: {invite_link}"

    if isinstance(event, CallbackQuery):
        await event.message.answer_photo(input_file, caption=caption, reply_markup=back)
    else:
        await event.answer_photo(input_file, caption=caption, reply_markup=back)

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

    ref_owner = await UsersDAO.find_by_tg_id(invite.owner_id)
    if not ref_owner:
        print(f"track_invites: no ref_owner found for owner_id={invite.owner_id}")
        return

    user = await UsersDAO.find_by_tg_id(event.from_user.id)
    if not user:
        print(f"track_invites: no user found for tg_id={event.from_user.id}, creating new user")
        user = await UsersDAO.add_user(tg_id=event.from_user.id, username=event.from_user.username or f"user_{event.from_user.id}")

    print(f"track_invites: updating user id={user.id}, tg_id={event.from_user.id} with invite_link={event.invite_link.invite_link}, invited_by={ref_owner.username}")
    await UsersDAO.update(user.id, invite_link=event.invite_link.invite_link, invited_by=ref_owner.username)

@router.message()
async def mes(message: Message):
    print(message.chat.id)