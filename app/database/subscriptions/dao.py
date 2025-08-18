from sqlalchemy import select
from app.database.db import async_session_maker
from app.dao.base import BaseDAO
from app.database.subscriptions.models import Subscription, SubscriptionType
from datetime import datetime, timedelta

class SubscriptionsDAO(BaseDAO):
    model = Subscription

    @classmethod
    async def add_subscription(cls, user_id: int, type_sub: SubscriptionType, referral_link_used: str = None, expires_at: datetime = None):
        async with async_session_maker() as session:
            try:
                now = datetime.now()
                sub = cls.model(
                    user_id=user_id,
                    type_sub=type_sub,
                    referral_link_used=referral_link_used,
                    created_at=now,
                    expires_at=expires_at
                )
                session.add(sub)
                await session.commit()
                await session.refresh(sub)
                return sub
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при добавлении подписки: {e}")
                return None

    @classmethod
    async def get_active_subscription(cls, user_id: int):
        async with async_session_maker() as session:
            now = datetime.now()
            query = select(cls.model).filter(
                cls.model.user_id == user_id,
                (cls.model.expires_at == None) | (cls.model.expires_at > now)
            )
            result = await session.execute(query)
            return result.scalars().first()
