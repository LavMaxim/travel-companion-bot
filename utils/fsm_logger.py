from aiogram.fsm.context import FSMContext
from logging import Logger

async def set_state_and_log(fsm: FSMContext, new_state: str, logger: Logger, user_id: int):
    old = await fsm.get_state()
    await fsm.set_state(new_state)
    new = await fsm.get_state()
    logger.info("FSM ▶ %s → %s for user %s", old, new, user_id)
