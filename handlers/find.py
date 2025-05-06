from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import (
    get_trips_by_date_category,
    get_trips_by_purpose,
    get_trips_by_companions,
    get_trips_by_location_keyword,
    get_random_trips,
    get_user_by_id
)
from keyboards.trip import get_trip_keyboard
from texts.trip import format_trip_card
from texts.trip import format_trip_card
from database import get_user_by_id
from keyboards.trip import get_trip_keyboard

router = Router()

@router.message(Command("find"))
async def show_find_menu(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Поиск по дате", callback_data="filter:date")],
        [InlineKeyboardButton(text="🎯 Поиск по цели", callback_data="filter:purpose")],
        [InlineKeyboardButton(text="🧍 Поиск по попутчикам", callback_data="filter:companions")],
        [InlineKeyboardButton(text="🌍 Поиск по направлению", callback_data="filter:location")],
        [InlineKeyboardButton(text="🎲 Случайные поездки", callback_data="filter:random")]
    ])
    await message.answer("🔎 Выберите параметр поиска:", reply_markup=keyboard)

# Общая функция для вывода карточек
async def send_trip_card(trip: tuple, callback_or_message):
    (
        rowid, user_id, username, country, location,
        date_from, date_to, purpose, companions,
        description, insert_dttm
    ) = trip

    author = get_user_by_id(user_id)
    text = format_trip_card(trip, author)

    reply_markup = get_trip_keyboard(user_id, rowid, username)

    await callback_or_message.answer(
        text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# Фильтр по дате
@router.callback_query(F.data == "filter:date")
async def show_date_options(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Сегодня", callback_data="filter:date:today")],
        [InlineKeyboardButton(text="📆 Завтра", callback_data="filter:date:tomorrow")],
        [InlineKeyboardButton(text="🗓 Выходные", callback_data="filter:date:weekend")],
        [InlineKeyboardButton(text="📅 Этот месяц", callback_data="filter:date:this_month")],
        [InlineKeyboardButton(text="📅 След. месяц", callback_data="filter:date:next_month")],
        [InlineKeyboardButton(text="📌 Гибкие даты", callback_data="filter:date:flexible")]
    ])
    await callback.message.edit_text("📅 Выберите диапазон дат:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("filter:date:"))
async def filter_by_date(callback: CallbackQuery):
    category = callback.data.split(":")[2]
    trips = get_trips_by_date_category(category)
    if not trips:
        await callback.message.edit_text("❌ Поездки по выбранной дате не найдены.")
        return
    await callback.message.edit_text(f"📅 Поездки по фильтру <b>{category}</b>:", parse_mode="HTML")
    for trip in trips[:3]:
        await send_trip_card(trip, callback.message)

# Фильтр по цели
@router.callback_query(F.data == "filter:purpose")
async def show_purpose_options(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏖 Отдых", callback_data="filter:purpose:отдых")],
        [InlineKeyboardButton(text="🧗 Приключения", callback_data="filter:purpose:приключения")],
        [InlineKeyboardButton(text="🚚 Переезд", callback_data="filter:purpose:переезд")],
        [InlineKeyboardButton(text="💼 Работа", callback_data="filter:purpose:работа")]
    ])
    await callback.message.edit_text("🎯 Выберите цель поездки:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("filter:purpose:"))
async def filter_by_purpose(callback: CallbackQuery):
    purpose = callback.data.split(":")[2]
    trips = get_trips_by_purpose(purpose)
    if not trips:
        await callback.message.edit_text("❌ Нет поездок с такой целью.")
        return
    await callback.message.edit_text(f"🎯 Цель: <b>{purpose}</b>", parse_mode="HTML")
    for trip in trips[:3]:
        await send_trip_card(trip, callback.message)

# Фильтр по попутчикам
@router.callback_query(F.data == "filter:companions")
async def show_companion_options(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙋‍♀️ Только девушки", callback_data="filter:companions:только девушки")],
        [InlineKeyboardButton(text="👫 Группа", callback_data="filter:companions:группа")],
        [InlineKeyboardButton(text="👥 1–2 человека", callback_data="filter:companions:1–2 человека")],
        [InlineKeyboardButton(text="❓ Не важно", callback_data="filter:companions:не важно")]
    ])
    await callback.message.edit_text("🧍 Выберите попутчиков:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("filter:companions:"))
async def filter_by_companions(callback: CallbackQuery):
    value = callback.data.split(":")[2]
    trips = get_trips_by_companions(value)
    if not trips:
        await callback.message.edit_text("❌ Ничего не найдено по параметру.")
        return
    await callback.message.edit_text(f"🧍 Попутчики: <b>{value}</b>", parse_mode="HTML")
    for trip in trips[:3]:
        await send_trip_card(trip, callback.message)

# Фильтр по направлению
@router.callback_query(F.data == "filter:location")
async def show_location_options(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏔 Сочи", callback_data="filter:location:Сочи")],
        [InlineKeyboardButton(text="🌴 Бали", callback_data="filter:location:Бали")],
        [InlineKeyboardButton(text="🇹🇷 Стамбул", callback_data="filter:location:Стамбул")],
        [InlineKeyboardButton(text="🇹🇭 Пхукет", callback_data="filter:location:Пхукет")],
        [InlineKeyboardButton(text="✏ Ввести вручную", callback_data="filter:location:manual")]
    ])
    await callback.message.edit_text("🌍 Выберите направление:", reply_markup=keyboard)

@router.callback_query(F.data == "filter:location:manual")
async def ask_for_location_input(callback: CallbackQuery):
    await callback.message.edit_text("✏ Введите город, начиная с `!`, например: `!сочи`", parse_mode="Markdown")

@router.callback_query(F.data.startswith("filter:location:"))
async def filter_by_location(callback: CallbackQuery):
    location = callback.data.split(":")[2]
    trips = get_trips_by_location_keyword(location)
    if not trips:
        await callback.message.edit_text("❌ По направлению ничего не найдено.")
        return
    await callback.message.edit_text(f"🌍 Направление: <b>{location}</b>", parse_mode="HTML")
    for trip in trips[:3]:
        await send_trip_card(trip, callback.message)

@router.message(F.text.startswith("!"))
async def find_by_location(message: Message):
    query = message.text[1:].strip()
    trips = get_trips_by_location_keyword(query)
    if not trips:
        await message.answer("❌ По направлению ничего не найдено.")
        return
    await message.answer(f"🌍 Направление: <b>{query}</b>", parse_mode="HTML")
    for trip in trips[:3]:
        await send_trip_card(trip, message)

# Случайные поездки
@router.callback_query(F.data == "filter:random")
async def show_random_trips(callback: CallbackQuery):
    trips = get_random_trips(limit=3)
    if not trips:
        await callback.message.edit_text("📭 Случайные поездки не найдены.")
        return
    await callback.message.edit_text("🎲 Вот несколько случайных поездок:")
    for trip in trips:
        await send_trip_card(trip, callback.message)
