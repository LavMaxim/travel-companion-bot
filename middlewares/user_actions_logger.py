# middlewares/user_actions_logger.py
from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext
from logger import get_logger

logger = get_logger(__name__)

class UserActionLoggerMiddleware(BaseMiddleware):
    """
    Outer-middleware: логируем все Message и CallbackQuery до фильтров.
    """
    async def __call__(self, handler, event, data):
        # Текущее FSM-состояние (если используется)
        fsm: FSMContext | None = data.get("state")
        state = await fsm.get_state() if fsm else None

        if isinstance(event, types.Message):
            logger.info(
                "USER_ACTION ▶ user_id=%s type=Message state=%s text=%s",
                event.from_user.id, state, event.text or "<empty>"
            )
        elif isinstance(event, types.CallbackQuery):
            logger.info(
                "USER_ACTION ▶ user_id=%s type=CallbackQuery state=%s data=%s",
                event.from_user.id, state, event.data or "<empty>"
            )

        return await handler(event, data)
