# handlers/fallback.py
from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()

@router.message()
async def fallback_message(message: Message):
    # Универсальный ответ на любой текст, который не попал ни в один хэндлер
    await message.answer(
        "Извините, я не понял ваш запрос. "
        "Воспользуйтесь /help, чтобы увидеть список доступных команд."
    )

@router.callback_query()
async def fallback_callback(callback: CallbackQuery):
    # Неброское уведомление при нажатии «неправильных» кнопок
    await callback.answer(
        "Эта кнопка сейчас неактивна.",
        show_alert=False  # просто исчезнет через пару секунд
    )
