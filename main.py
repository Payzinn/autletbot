import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from app.routers.user import router as user_router
from app.routers.admin import router as admin_router

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except:
        print("Exit")
