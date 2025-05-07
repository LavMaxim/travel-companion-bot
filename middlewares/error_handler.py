import traceback

from aiogram import BaseMiddleware, types
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery

from logger import get_logger
from config import ADMINS  # предполагается, что ADMINS = [id1, id2, ...]

logger = get_logger(__name__)

class ErrorLoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования неожиданных ошибок и уведомления администраторов.
    """
    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception as e:
            # Стектрейс в логи
            tb_str = traceback.format_exc()
            logger.exception("❌ Exception in handler:\n%s", tb_str)

            # Краткое сообщение админам
            text = (
                f"❌ <b>Ошибка в боте</b>\n"
                f"<pre>{e}</pre>\n"
                f"<i>См. полный стектрейс в bot_errors.log</i>"
            )

            # Отправляем каждому администратору
            for admin_id in ADMINS:
                try:
                    # Если это callback — извлечь текст, иначе для message
                    if isinstance(event, CallbackQuery):
                        await event.bot.send_message(admin_id, text, parse_mode="HTML")
                    elif isinstance(event, Message):
                        await event.bot.send_message(admin_id, text, parse_mode="HTML")
                    else:
                        # универсальный способ
                        await event.bot.send_message(admin_id, text, parse_mode="HTML")
                except Exception as notify_err:
                    # Не позволяем рекурсии ошибок
                    logger.error("Не удалось уведомить админа %s: %s", admin_id, notify_err)
            # Рерэйзить или подавлять? Здесь — подавляем, чтобы бот не падал
            return
