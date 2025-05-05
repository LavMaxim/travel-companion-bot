import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from logger import logger
from database import init_db
from handlers import create_trip, cancel, trips, admin, mytrips, find, join, menu, find_menu, profile
from middlewares.error_handler import ErrorLoggingMiddleware
from middlewares.user_actions_logger import UserActionLoggerMiddleware

# Загрузка переменных окружения
load_dotenv(dotenv_path="O:/Telegrambot/.env")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота и диспетчера
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение роутеров
dp.include_router(menu.router)
dp.include_router(create_trip.router)
dp.include_router(cancel.router)
dp.include_router(trips.router)
dp.include_router(admin.router)
dp.include_router(mytrips.router)
dp.include_router(find.router)
dp.include_router(join.router)
dp.include_router(profile.router)

# Middleware ошибок
dp.message.middleware(ErrorLoggingMiddleware())
dp.callback_query.middleware(ErrorLoggingMiddleware())

#логирование действий
dp.message.middleware(UserActionLoggerMiddleware())
dp.callback_query.middleware(UserActionLoggerMiddleware())

# Точка входа
async def main():
    try:
        init_db()
        print("🧰 Бот запущен!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("❌ Unhandled exception in main loop")

if __name__ == "__main__":
    asyncio.run(main())
""