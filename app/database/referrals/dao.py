from sqlalchemy import select, insert, update
from app.database.db import async_session_maker
from app.database.referrals.models import Referrals, ReferralStatus
from app.dao.base import BaseDAO
from app.database.invites.models import Invite
from datetime import datetime
from datetime import date

class ReferralsDAO(BaseDAO):
    model = Referrals

    @classmethod
    async def add_referral(cls, user_id: int, referral_link: str, status: ReferralStatus = ReferralStatus.ACTIVE):
        async with async_session_maker() as session:
            try:
                query = cls.model(user_id=user_id, referral_link=referral_link, status=status)
                session.add(query)
                await session.commit()
                await session.refresh(query)
                return query.id  
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при добавлении реферала: {type(e).__name__} - {str(e)}")
                return None

    @classmethod
    async def find_by_user_id(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            return result.scalars().all()
    
    @classmethod
    async def find_by_user_id_active(cls, user_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.user_id == user_id)
                .where(cls.model.status == ReferralStatus.ACTIVE)
            )
            result = await session.execute(query)
            referral = result.scalars().first()
            return referral
        
    @classmethod
    async def find_by_user_id_all(cls, user_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.user_id == user_id)
                .where(cls.model.status.in_([ReferralStatus.ACTIVE, ReferralStatus.DISABLED]))
            )
            result = await session.execute(query)
            referral = result.scalars().all()
            return referral

    @classmethod
    async def update_status(cls, referral_id: int, status: ReferralStatus):
        async with async_session_maker() as session:
            try:
                query = (
                    update(cls.model)
                    .where(cls.model.id == referral_id)
                    .values(status=status)
                )
                await session.execute(query)
                await session.commit()

                result = await session.execute(select(cls.model).where(cls.model.id == referral_id))
                return result.scalars().first()
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при обновлении статуса реферала: {type(e).__name__} - {str(e)}")
                return None