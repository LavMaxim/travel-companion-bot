import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

logger = logging.getLogger(__name__)

class UserActionLoggerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = None

        if isinstance(event, Message):
            user = event.from_user
            logger.info(f"[MSG] {user.id} | {user.full_name} | {event.text}")
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(f"[CBQ] {user.id} | {user.full_name} | data={event.data}")

        return await handler(event, data)
