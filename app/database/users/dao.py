from sqlalchemy import select, insert
from app.database.db import async_session_maker
from app.database.users.models import Users
from app.dao.base import BaseDAO
from app.database.invites.models import Invite
from datetime import datetime
from datetime import date

class UsersDAO(BaseDAO):
    model = Users 

    @classmethod
    async def add_user(cls,
                       tg_id: int, 
                       username: str, 
                       referral_link: str = None, 
                       invite_link: str = None, 
                       invited_by: str = None):
        async with async_session_maker() as session:
            try:
                query = cls.model(username=username, 
                                tg_id=tg_id, 
                                referral_link=referral_link, 
                                invited_by=invited_by, 
                                invite_link=invite_link,
                                created_at=datetime.now(), 
                                updated_at=datetime.now()
                                )
                session.add(query)
                await session.commit()
                await session.refresh(query)
                return query # Возвращается именно объект, чтобы было легче работать с ним
            except Exception as e:
                await session.rollback()
                print(e)
                return None
    
    @classmethod
    async def find_by_referral_link(cls, link: str):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(referral_link=link)
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
            query = select(Users.referral_link).join(Invite, Invite.owner_id == Users.id).filter(Invite.invite_link == invite_link)
            result = await session.execute(query)
            return result.scalars().first()