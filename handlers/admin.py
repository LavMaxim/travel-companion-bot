from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMINS
from database import get_all_trips, delete_trip, delete_trips_by_user
import re
from texts.trip import format_trip_card

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("❌ У тебя нет доступа к админке.")
        return

    trips = get_all_trips()
    if not trips:
        await message.answer("📭 В базе пока пусто.")
        return

    text = f"📋 Всего поездок в базе: <b>{len(trips)}</b>\n"
    text += "Напиши <code>/delete 3</code> — удалить поездку по ID\n"
    text += "Или <code>/delete u123456789</code> — удалить все поездки пользователя\n"
    await message.answer(text, parse_mode="HTML")


@router.message(Command("delete"))
async def delete_trip_cmd(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("❌ У тебя нет доступа к удалению.")
        return

    text = message.text.strip()

    # Удаление по user_id — /delete u123456789
    match_user = re.match(r"/delete\s+u(\d+)", text)
    if match_user:
        user_id = int(match_user.group(1))
        count = delete_trips_by_user(user_id)
        if count > 0:
            await message.answer(f"✅ Удалено поездок от пользователя {user_id}: {count}")
        else:
            await message.answer(f"❌ У пользователя {user_id} нет поездок.")
        return

    # Удаление по trip ID — /delete 5
    match_trip = re.match(r"/delete\s+(\d+)", text)
    if match_trip:
        trip_id = int(match_trip.group(1))
        success = delete_trip(trip_id)
        if success:
            await message.answer(f"✅ Поездка с ID {trip_id} удалена.")
        else:
            await message.answer(f"❌ Поездка с ID {trip_id} не найдена.")
        return

    # Неверный формат
    await message.answer(
        "⚠ Укажи ID поездки или пользователя.\n\n"
        "<code>/delete 3</code> — удалить одну поездку\n"
        "<code>/delete u123456789</code> — удалить ВСЕ поездки пользователя",
        parse_mode="HTML"
    )
