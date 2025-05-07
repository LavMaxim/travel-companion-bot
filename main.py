import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db
from handlers import (
    create_trip,
    cancel,
    admin,
    mytrips,
    find,
    join,
    menu,
    profile,
    register,
    fallback,
    help
)
from middlewares.error_handler import ErrorLoggingMiddleware
from middlewares.user_actions_logger import UserActionLoggerMiddleware

from logger import get_logger

logger = get_logger(__name__)

# Подгружаем .env из текущей рабочей директории
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is not set in environment variables")
    exit(1)


async def main():
    # Инициализация БД
    init_db()
    logger.info("🧰 База данных инициализирована")

    # Создаём бот и диспетчер
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все роутеры
    for router in (
        menu.router,
        create_trip.router,
        cancel.router,
        admin.router,
        mytrips.router,
        find.router,
        join.router,
        profile.router,
        register.router,
        help.router,
    ):
        dp.include_router(router)

    # отдельно подключаем отбивку для неизвестных команд
    for router in (
        fallback.router,
    ):
        dp.include_router(router)

    # Middleware для отлова ошибок и логирования действий
    dp.message.middleware(ErrorLoggingMiddleware())
    dp.callback_query.middleware(ErrorLoggingMiddleware())

    # Middleware для логирования действий
    dp.message.outer_middleware(UserActionLoggerMiddleware())
    dp.callback_query.outer_middleware(UserActionLoggerMiddleware())

    
    logger.info("🚀 Старт polling")
    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception("❌ Необработанное исключение в основном цикле")


if __name__ == "__main__":
    asyncio.run(main())
