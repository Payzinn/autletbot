from aiogram.filters.callback_data import CallbackData

class ReferralLink(CallbackData, prefix="referral_link"):
    link: str