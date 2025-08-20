from sqlalchemy import select, insert, update
from app.database.db import async_session_maker
from app.database.users.models import Users
from app.database.referrals.models import Referrals 
from app.dao.base import BaseDAO
from app.database.invites.models import Invite
from datetime import datetime
from datetime import date

class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def add_user(cls, tg_id: int, username: str, referral_link_id: int = None, invite_link: str = None, invited_by: str = None):
        async with async_session_maker() as session:
            try:
                query = cls.model(
                    username=username,
                    tg_id=tg_id,
                    referral_link=referral_link_id,
                    invite_link=invite_link,
                    invited_by=invited_by,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(query)
                await session.commit()
                await session.refresh(query)
                return query
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при добавлении пользователя: {e}")
                return None

    @classmethod
    async def find_by_tg_id(cls, tg_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(tg_id=tg_id)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_by_username(cls, username: str):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(username=username)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_referral_by_invite_link(cls, invite_link: str):
        async with async_session_maker() as session:
            query = (
                select(Referrals.referral_link)
                .join(Users, Users.id == Invite.owner_id)
                .join(Referrals, Referrals.user_id == Users.id)
                .filter(Invite.invite_link == invite_link)
            )
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def update(cls, user_id: int, **kwargs):
        async with async_session_maker() as session:
            try:
                query = (
                    update(cls.model)
                    .where(cls.model.id == user_id)
                    .values(**kwargs, updated_at=datetime.now())
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при обновлении пользователя: {e}")
                return None