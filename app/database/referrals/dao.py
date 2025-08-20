from sqlalchemy import select, insert, update
from app.database.db import async_session_maker
from app.database.referrals.models import Referrals
from app.dao.base import BaseDAO
from app.database.invites.models import Invite
from datetime import datetime
from datetime import date

class ReferralsDAO(BaseDAO):
    model = Referrals

    @classmethod
    async def add_referral(cls, user_id: int, referral_link: str, status: str = "active"):
        async with async_session_maker() as session:
            try:
                query = cls.model(user_id=user_id, referral_link=referral_link, status=status)
                session.add(query)
                await session.commit()
                await session.refresh(query)
                return query.id  
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при добавлении реферала: {e}")
                return None

    @classmethod
    async def find_by_user_id(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def update_status(cls, referral_id: int, status: str):
        async with async_session_maker() as session:
            try:
                query = (
                    update(cls.model)
                    .where(cls.model.id == referral_id)
                    .values(status=status)
                )
                await session.execute(query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при обновлении статуса реферала: {e}")
                return None