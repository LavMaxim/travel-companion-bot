from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from texts.trip import format_trip_card

router = Router()

@router.callback_query(F.data.startswith("join:"))
async def handle_join(callback: CallbackQuery, bot: Bot):
    _, target_user_id, trip_id = callback.data.split(":")
    target_user_id = int(target_user_id)
    from_user = callback.from_user

    # Пользователь не может присоединиться к своей поездке
    if from_user.id == target_user_id:
        await callback.answer("⚠ Это твоя поездка!", show_alert=True)
        return

    # Попробуем отправить сообщение автору поездки
    try:
        text = (
            f"📩 <b>{from_user.full_name}</b> (@{from_user.username or 'без username'}) "
            f"хочет присоединиться к твоей поездке #{trip_id}!"
        )
        await bot.send_message(chat_id=target_user_id, text=text, parse_mode="HTML")
    except TelegramBadRequest:
        await callback.answer("❌ Невозможно связаться с автором поездки.")
        return

    await callback.answer("✅ Заявка отправлена автору поездки!", show_alert=True)
