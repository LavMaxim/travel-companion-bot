from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import (
    get_trips_by_date_category,
    get_trips_by_purpose,
    get_trips_by_companions,
    get_trips_by_location_keyword,
    get_random_trips
)
from keyboards.trip import get_trip_keyboard


router = Router()

# 💬 Универсальный формат карточки поездки
def format_trip_card(trip: tuple) -> str:
    (
        rowid, user_id, username, country, location,
        date_from, date_to, purpose, companions,
        description, insert_dttm
    ) = trip
    username_display = f"@{username}" if username else "<i>аноним</i>"
    return (
        f"👤 <b>Автор:</b> {username_display}\n"
        f"🌍 <b>Страна:</b> {country or '—'}\n"
        f"🌍 <b>Место:</b> {location or '—'}\n"
        f"📅 <b>С:</b> {date_from or '—'}\n"
        f"📅 <b>По:</b> {date_to or '—'}\n"
        f"🎯 <b>Цель:</b> {purpose or '—'}\n"
        f"🧍 <b>Спутники:</b> {companions or '—'}\n"
        f"📝 <b>Описание:</b> {description or '—'}\n"
        f"⏱ <b>Добавлено:</b> {insert_dttm or '—'}"
    )



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


# 🔎 Поиск по дате
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
        rowid, user_id, username, *_ = trip
        await callback.message.answer(
            format_trip_card(trip),
            parse_mode="HTML",
            reply_markup=get_trip_keyboard(user_id, rowid, username)
)


# 🔎 Поиск по цели
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
        rowid, user_id, username, *_ = trip
        await callback.message.answer(
            format_trip_card(trip),
            parse_mode="HTML",
            reply_markup=get_trip_keyboard(user_id, rowid, username)
)

# 🔎 Поиск по попутчикам
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
        rowid, user_id, username, *_ = trip
        await callback.message.answer(
            format_trip_card(trip),
            parse_mode="HTML",
            reply_markup=get_trip_keyboard(user_id, rowid, username)
        )

# 🔎 Поиск по направлению
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
        rowid, user_id, username, *_ = trip
        await callback.message.answer(
            format_trip_card(trip),
            parse_mode="HTML",
            reply_markup=get_trip_keyboard(user_id, rowid, username)
)


@router.message(F.text.startswith("!"))
async def find_by_location(message: Message):
    query = message.text[1:].strip()
    trips = get_trips_by_location_keyword(query)
    if not trips:
        await message.answer("❌ По направлению ничего не найдено.")
        return
    await message.answer(f"🌍 Направление: <b>{query}</b>", parse_mode="HTML")
    for trip in trips[:3]:
        rowid, user_id, username, *_ = trip
        await message.answer(
            format_trip_card(trip),
            parse_mode="HTML",
            reply_markup=get_trip_keyboard(user_id, rowid, username)
        )

# 🔎 Случайные поездки
@router.callback_query(F.data == "filter:random")
async def show_random_trips(callback: CallbackQuery):
    trips = get_random_trips(limit=3)
    if not trips:
        await callback.message.edit_text("📭 Случайные поездки не найдены.")
        return
    await callback.message.edit_text("🎲 Вот несколько случайных поездок:")
    for trip in trips:
        rowid, user_id, username, *_ = trip
        await callback.message.answer(
            format_trip_card(trip),
            parse_mode="HTML",
            reply_markup=get_trip_keyboard(user_id, rowid, username)
        )
FILTER_KEYS = {
    "date": "Дата",
    "purpose": "Цель",
    "companions": "Попутчики",
    "location": "Направление"
}

async def update_filter_message(callback: CallbackQuery, user_id: int):
    filters = user_filters.get(user_id, {})
    trips = get_trips_with_filters(filters)

    page = pagination_state.get(user_id, 0)
    per_page = 3
    shown_trips = trips[page * per_page: (page + 1) * per_page]

    # Сформируем текст
    filter_text = "🔎 <b>Активные фильтры:</b>\n"
    if not filters:
        filter_text += "— Нет\n"
    else:
        for key, value in filters.items():
            filter_text += f"• {FILTER_KEYS.get(key, key)}: {value} [удалить:{key}]\n"

    trip_texts = [
        f"🌍 <b>{t[3]}</b>\n📅 {t[4]} — {t[5]}\n🎯 {t[6]}\n🧍 {t[7]}\n📝 {t[8]}"
        for t in shown_trips
    ]

    combined_text = filter_text + "\n\n" + "\n\n".join(trip_texts) if trip_texts else filter_text + "\n\n❌ Поездки не найдены."

    # Кнопки
    buttons = []

    if filters:
        buttons.append([InlineKeyboardButton(text="🔁 Сбросить все", callback_data="reset_filters")])
        for key in filters:
            buttons.append([InlineKeyboardButton(text=f"❌ Убрать {FILTER_KEYS.get(key)}", callback_data=f"remove_filter:{key}")])

    if (page + 1) * per_page < len(trips):
        buttons.append([InlineKeyboardButton(text="▶ Показать ещё", callback_data="show_more")])

    await callback.message.edit_text(
        combined_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


        
# Обработчики примера:
@router.callback_query(F.data.startswith("add_filter:"))
async def add_filter(callback: CallbackQuery):
    user_id = callback.from_user.id
    _, key, value = callback.data.split(":")

    user_filters.setdefault(user_id, {})[key] = value
    pagination_state[user_id] = 0
    await update_filter_message(callback, user_id)

@router.callback_query(F.data.startswith("remove_filter:"))
async def remove_filter(callback: CallbackQuery):
    user_id = callback.from_user.id
    key = callback.data.split(":")[1]
    user_filters.get(user_id, {}).pop(key, None)
    pagination_state[user_id] = 0
    await update_filter_message(callback, user_id)

@router.callback_query(F.data == "reset_filters")
async def reset_all(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_filters[user_id] = {}
    pagination_state[user_id] = 0
    await update_filter_message(callback, user_id)

@router.callback_query(F.data == "show_more")
async def show_more(callback: CallbackQuery):
    user_id = callback.from_user.id
    pagination_state[user_id] += 1
    await update_filter_message(callback, user_id)