from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import get_all_trips

router = Router()

@router.message(Command("trips"))
async def show_all_trips(message: Message):
    trips = get_all_trips()
    if not trips:
        await message.answer("❌ Пока нет ни одного предложения.")
        return

    for trip in trips:
        rowid, user_id, username, location, date, purpose, companions, description = trip
        text = (
            f"🌍 <b>Место:</b> {location}\n"
            f"📅 <b>Даты:</b> {date}\n"
            f"🎯 <b>Цель:</b> {purpose}\n"
            f"🧍 <b>Спутники:</b> {companions}\n"
            f"📝 <b>Описание:</b> {description}"
        )

        # Генерируем кнопки
        buttons = [
            [InlineKeyboardButton(text="📩 Присоединиться", callback_data=f"join:{user_id}:{rowid}")]
        ]

        if username:
            buttons.append([
                InlineKeyboardButton(
                    text="👤 Профиль автора",
                    url=f"https://t.me/{username}"
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
