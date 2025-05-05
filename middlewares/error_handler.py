from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Dict, Any
from logger import logger

class ErrorLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception(f"❌ Unhandled error: {e}")
            # можно уведомить пользователя, если нужно:
            if "event_from_user" in data:
                try:
                    await data["event_from_user"].answer("⚠ Произошла внутренняя ошибка.")
                except:
                    pass
