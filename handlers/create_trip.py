from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from states.trip import FSMTrip
from database import save_trip
from keyboards.trip import (
    get_country_keyboard, get_city_keyboard,
    get_date_keyboard, get_purpose_keyboard, get_companions_keyboard
)
from texts.trip import (
    date_from_hint, date_to_hint,
    purpose_hint, purpose_manual_hint,
    companions_hint, companions_manual_hint,
    description_hint, description_too_long
)
from texts.trip import format_trip_card
from datetime import datetime, timedelta
import re

from logger import get_logger
from utils.fsm_logger import set_state_and_log

router = Router()
logger = get_logger(__name__)

@router.message(Command("create"))
async def start_trip_creation(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Переход в первое состояние
    await set_state_and_log(state, FSMTrip.country, logger, user_id)
    await message.answer(
        "🌍 Введите страну, в которую хотели бы поехать:",
        reply_markup=get_country_keyboard()
    )

@router.callback_query(F.data.startswith("country:"))
async def handle_country(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    country = callback.data.split(":")[1]
    await state.update_data(country=country)
    # Переход к выбору города
    await set_state_and_log(state, FSMTrip.city, logger, user_id)
    await callback.message.edit_text(
        f"🇨🇭 Вы выбрали страну: {country}. Теперь выберите город:",
        reply_markup=get_city_keyboard(country)
    )

@router.callback_query(F.data.startswith("city:"))
async def handle_city(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    city = callback.data.split(":")[1]
    await state.update_data(location=city)
    # Переход к дате начала
    await set_state_and_log(state, FSMTrip.date_from, logger, user_id)
    await callback.message.edit_text(f"📍 Вы выбрали город: {city}")
    await callback.message.answer(
        date_from_hint,
        reply_markup=get_date_keyboard("date_from")
    )

@router.callback_query(F.data.startswith("date_from:"))
async def handle_date_from(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    value = callback.data.split(":")[1]
    date = parse_date_shortcut(value)
    await state.update_data(date_from=date)
    await callback.message.edit_text(
        f"📅 Дата начала: <b>{date}</b>", parse_mode="HTML"
    )
    # Переход к дате окончания
    await set_state_and_log(state, FSMTrip.date_to, logger, user_id)
    await callback.message.answer(
        date_to_hint,
        reply_markup=get_date_keyboard("date_to")
    )

@router.callback_query(F.data.startswith("date_to:"))
async def handle_date_to(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    value = callback.data.split(":")[1]
    date = parse_date_shortcut(value, to=True)
    await state.update_data(date_to=date)
    await callback.message.edit_text(
        f"📅 Дата окончания: <b>{date}</b>", parse_mode="HTML"
    )
    # Переход к выбору цели
    await set_state_and_log(state, FSMTrip.purpose, logger, user_id)
    await callback.message.answer(
        purpose_hint,
        reply_markup=get_purpose_keyboard()
    )

@router.message(FSMTrip.date_from)
@router.message(FSMTrip.date_to)
async def handle_manual_date(message: Message, state: FSMContext):
    # Парсим ручной ввод дат
    text = message.text.strip()
    try:
        datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        await message.answer(date_format_error)
        return

    current = await state.get_state()
    user_id = message.from_user.id
    if current == FSMTrip.date_from.state:
        await state.update_data(date_from=text)
        # Переход к дате окончания
        await set_state_and_log(state, FSMTrip.date_to, logger, user_id)
        await message.answer(
            date_to_hint, reply_markup=get_date_keyboard("date_to")
        )
    else:
        await state.update_data(date_to=text)
        # Переход к выбору цели
        await set_state_and_log(state, FSMTrip.purpose, logger, user_id)
        await message.answer(
            purpose_hint, reply_markup=get_purpose_keyboard()
        )

@router.callback_query(F.data.startswith("purpose:"))
async def handle_purpose(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    value = callback.data.split(":")[1]
    if value == "manual":
        await callback.message.edit_text(purpose_manual_hint)
        return
    await state.update_data(purpose=value)
    # Переход к выбору попутчиков
    await set_state_and_log(state, FSMTrip.companions, logger, user_id)
    await callback.message.edit_text(f"🎯 Цель поездки: {value}")
    await callback.message.answer(companions_hint, reply_markup=get_companions_keyboard())

@router.message(FSMTrip.purpose)
async def set_purpose_manual(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(purpose=message.text)
    # Переход к выбору попутчиков
    await set_state_and_log(state, FSMTrip.companions, logger, user_id)
    await message.answer(companions_hint, reply_markup=get_companions_keyboard())

@router.callback_query(F.data.startswith("companions:"))
async def handle_companions(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    value = callback.data.split(":")[1]
    if value == "manual":
        await callback.message.edit_text(companions_manual_hint)
        return
    await state.update_data(companions=value)
    # Переход к описанию
    await set_state_and_log(state, FSMTrip.description, logger, user_id)
    await callback.message.edit_text(f"🧍 Попутчики: {value}")
    await callback.message.answer(description_hint)

@router.message(FSMTrip.companions)
async def set_companions_manual(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(companions=message.text)
    # Переход к описанию
    await set_state_and_log(state, FSMTrip.description, logger, user_id)
    await message.answer(description_hint)

@router.message(FSMTrip.description)
async def set_description(message: Message, state: FSMContext):
    text = message.text.strip()
    if len(text) > 300:
        await message.answer(description_too_long)
        return

    user_id = message.from_user.id
    await state.update_data(description=text)
    data = await state.get_data()

    save_trip(
        user_id=user_id,
        username=message.from_user.username,
        data=data
    )

    card = format_trip_card(data)
    await message.answer(card, parse_mode="HTML")

    # Завершаем FSM
    old = await state.get_state()
    await state.clear()
    logger.info("FSM ▶ %s → %s for user %s", old, None, user_id)


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
