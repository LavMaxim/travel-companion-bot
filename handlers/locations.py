from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from data.locations import popular_locations
from aiogram import F
from aiogram.types import CallbackQuery
from database import search_trips_by_location

router = Router()

@router.message(Command("locations"))
async def show_locations(message: Message):
    # Генерируем кнопки по 2 в ряд
    buttons = []
    row = []
    for i, city in enumerate(popular_locations, 1):
        row.append(InlineKeyboardButton(text=city, callback_data=f"find:{city}"))
        if i % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("🌍 Выберите направление для поиска:", reply_markup=keyboard)



@router.callback_query(F.data.startswith("find:"))
async def search_location_callback(callback: CallbackQuery):
    query = callback.data.split(":", 1)[1]
    trips = search_trips_by_location(query)

    if not trips:
        await callback.message.answer(f"❌ Поездки по направлению «{query}» не найдены.")
        return

    for trip in trips:
        location, date, purpose, companions, description = trip
        text = (
            f"🌍 <b>Место:</b> {location}\n"
            f"📅 <b>Даты:</b> {date}\n"
            f"🎯 <b>Цель:</b> {purpose}\n"
            f"🧍 <b>Спутники:</b> {companions}\n"
            f"📝 <b>Описание:</b> {description}"
        )
        await callback.message.answer(text, parse_mode="HTML")

    await callback.answer()
