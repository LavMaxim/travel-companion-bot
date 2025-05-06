from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from states.trip import FSMTrip
from database import save_trip
from keyboards.trip import get_date_keyboard, get_purpose_keyboard, get_companions_keyboard
from texts.trip import (
    location_hint, date_format_error, date_from_hint, date_to_hint,
    purpose_hint, purpose_manual_hint, companions_hint, companions_manual_hint,
    description_hint, description_too_long
)
from datetime import datetime, timedelta
import re
from keyboards.trip import get_country_keyboard
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F
from keyboards.trip import get_city_keyboard
from texts.trip import format_trip_card

router = Router()

# 👉 Эту функцию можно вызывать из других файлов
async def start_trip_creation(message: Message, state: FSMContext):
    await state.set_state(FSMTrip.country)
    await message.answer("🌍 Введите страну, в которую хотели бы поехать:", reply_markup=get_country_keyboard())


@router.callback_query(F.data.startswith("country:"))
async def handle_country(callback: CallbackQuery, state: FSMContext):
    country = callback.data.split(":")[1]
    await state.update_data(country=country)
    await state.set_state(FSMTrip.city)
    await callback.message.edit_text(
        f"🇨🇭 Вы выбрали страну: {country}. Теперь выберите город:",
        reply_markup=get_city_keyboard(country)
    )

@router.callback_query(F.data.startswith("city:"))
async def handle_city(callback: CallbackQuery, state: FSMContext):
    city = callback.data.split(":")[1]
    await state.update_data(location=city)
    await callback.message.edit_text(f"📍 Вы выбрали город: {city}")
    await callback.message.answer(date_from_hint, reply_markup=get_date_keyboard("date_from"))
    await state.set_state(FSMTrip.date_from)


@router.callback_query(F.data.startswith("date_from:"))
async def handle_date_from(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":")[1]
    date = parse_date_shortcut(value)
    await state.update_data(date_from=date)
    await callback.message.edit_text(f"📅 Дата начала: <b>{date}</b>", parse_mode="HTML")
    await callback.message.answer(date_to_hint, reply_markup=get_date_keyboard("date_to"))
    await state.set_state(FSMTrip.date_to)

@router.callback_query(F.data.startswith("date_to:"))
async def handle_date_to(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":")[1]
    date = parse_date_shortcut(value, to=True)
    await state.update_data(date_to=date)
    await callback.message.edit_text(f"📅 Дата окончания: <b>{date}</b>", parse_mode="HTML")
    await callback.message.answer(purpose_hint, reply_markup=get_purpose_keyboard())
    await state.set_state(FSMTrip.purpose)

@router.message(FSMTrip.date_from)
@router.message(FSMTrip.date_to)
async def handle_manual_date(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        await message.answer(date_format_error)
        return

    current = await state.get_state()
    if current == FSMTrip.date_from.state:
        await state.update_data(date_from=text)
        await message.answer(date_to_hint, reply_markup=get_date_keyboard("to"))
        await state.set_state(FSMTrip.date_to)
    else:
        await state.update_data(date_to=text)
        await message.answer(purpose_hint, reply_markup=get_purpose_keyboard())
        await state.set_state(FSMTrip.purpose)

@router.callback_query(F.data.startswith("purpose:"))
async def handle_purpose(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":")[1]
    if value == "manual":
        await callback.message.edit_text(purpose_manual_hint)
        await state.set_state(FSMTrip.purpose)
        return
    await state.update_data(purpose=value)
    await callback.message.edit_text(f"🎯 Цель поездки: {value}")
    await callback.message.answer(companions_hint, reply_markup=get_companions_keyboard())
    await state.set_state(FSMTrip.companions)

@router.message(FSMTrip.purpose)
async def set_purpose_manual(message: Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    await message.answer(companions_hint, reply_markup=get_companions_keyboard())
    await state.set_state(FSMTrip.companions)

@router.callback_query(F.data.startswith("companions:"))
async def handle_companions(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":")[1]
    if value == "manual":
        await callback.message.edit_text(companions_manual_hint)
        await state.set_state(FSMTrip.companions)
        return
    await state.update_data(companions=value)
    await callback.message.edit_text(f"🧍 Попутчики: {value}")
    await callback.message.answer(description_hint, parse_mode="HTML")
    await state.set_state(FSMTrip.description)

@router.message(FSMTrip.companions)
async def set_companions_manual(message: Message, state: FSMContext):
    await state.update_data(companions=message.text)
    await message.answer(description_hint, parse_mode="HTML")
    await state.set_state(FSMTrip.description)

@router.message(FSMTrip.description)
async def set_description(message: Message, state: FSMContext):
    text = message.text.strip()
    if len(text) > 300:
        await message.answer(description_too_long)
        return

    await state.update_data(description=text)
    data = await state.get_data()

    save_trip(
        user_id=message.from_user.id,
        username=message.from_user.username,
        data=data
    )

    summary = (
        f"✅ <b>Поездка создана!</b>\n\n"
        f"<b>🌍 Страна :</b> {data['country']}\n"
        f"<b>🌍 Место:</b> {data['location']}\n"
        f"<b>📅 С:</b> {data['date_from']}\n"
        f"<b>📅 По:</b> {data['date_to']}\n"
        f"<b>🎯 Цель:</b> {data['purpose']}\n"
        f"<b>🧍 Попутчики:</b> {data['companions']}\n"
        f"<b>📝 Описание:</b> {data['description']}"
    )
    await message.answer(summary, parse_mode="HTML")
    await state.clear()

def parse_date_shortcut(code: str, to=False) -> str:
    now = datetime.now()
    if code == "today":
        return now.strftime("%d.%m.%Y")
    elif code == "tomorrow":
        return (now + timedelta(days=1)).strftime("%d.%m.%Y")
    elif code == "weekend":
        saturday = now + timedelta((5 - now.weekday()) % 7)
        return (saturday if not to else saturday + timedelta(days=1)).strftime("%d.%m.%Y")
    elif code == "this_month":
        last_day = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return (now if not to else last_day).strftime("%d.%m.%Y")
    elif code == "next_month":
        first_next = (now.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day = (first_next.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return (first_next if not to else last_day).strftime("%d.%m.%Y")
    elif code == "flexible":
        return "гибкие даты"
    return now.strftime("%d.%m.%Y")
