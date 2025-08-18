from sqlalchemy import select, update
from app.database.db import async_session_maker

class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model)
            execution = await session.execute(query)
            result = execution.scalars.all()
            return result
    
    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            execution = await session.execute(query)
            result = execution.scalars().one_or_none()
            return result
        
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            execution = await session.execute(query)
            result = execution.scalars().one_or_none()
            return result
    
        
    @classmethod
    async def find_by_filter(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            execution = await session.execute(query)
            result = execution.scalars().all()
            return result
    
    @classmethod
    async def update(cls, model_id: int, **fields):
        async with async_session_maker() as session:
            await session.execute(
                update(cls.model).where(cls.model.id == model_id).values(**fields)
            )
            await session.commit()