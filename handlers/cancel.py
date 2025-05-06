from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command
from texts.trip import format_trip_card

router = Router()

@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("❌ Нет активного процесса для отмены.")
        return
    await state.clear()
    await message.answer("🚫 Действие отменено.", reply_markup=ReplyKeyboardRemove())
