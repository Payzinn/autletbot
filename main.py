import asyncio
from aiogram import Bot, Dispatcher
from app.config import settings
from app.routers.user import router as user_router
import logging

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(user_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except:
        print("Exit")