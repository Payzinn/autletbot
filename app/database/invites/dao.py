from app.database.db import async_session_maker
from app.dao.base import BaseDAO
from app.database.invites.models import Invite
from datetime import datetime
from sqlalchemy import select

class InvitesDAO(BaseDAO):
    model = Invite

    @classmethod
    async def add_invite(cls, owner_id: int, invite_link: str, qr_code_path: str = None):
        async with async_session_maker() as session:
            try:
                new_invite = cls.model(
                    owner_id=owner_id,
                    invite_link=invite_link,
                    qr_code_path=qr_code_path,
                    created_at=datetime.now()
                )
                session.add(new_invite)
                await session.commit()
                await session.refresh(new_invite)
                return new_invite
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при добавлении инвайта: {e}")
                return None

    @classmethod
    async def find_by_owner(cls, owner_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(owner_id=owner_id)
            execution = await session.execute(query)
            return execution.scalars().all()
