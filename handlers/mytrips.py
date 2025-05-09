from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from database import get_trips_by_user, delete_trip_by_user
from texts.trip import format_trip_card
from database import get_user_by_id
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(Command("mytrips"))
async def show_my_trips(message: Message):
    user_id = message.from_user.id
    trips = get_trips_by_user(user_id)

    if not trips:
        await message.answer("📭 У тебя пока нет созданных поездок.")
        return

    author = get_user_by_id(user_id)

    for trip in trips:
        trip_id = trip[0]
        text = format_trip_card(trip, author, is_own=True)

        # Генерация диплинка на поездку
        trip_link = await create_start_link(message.bot, f"trip_{trip_id}", encode=True)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Поделиться", url=trip_link)],
                [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{trip_id}")]
            ]
        )

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("delete:"))
async def delete_trip_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    trip_id = int(callback.data.split(":")[1])

    success = delete_trip_by_user(trip_id, user_id)

    if success:
        await callback.message.edit_text("✅ Поездка удалена.")
    else:
        await callback.answer("❌ Нельзя удалить чужую поездку.", show_alert=True)


# Обёртка для вызова из других модулей
async def show_user_trips(message: Message):
    await show_my_trips(message)
