from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.locations import locations_by_country

def get_country_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=country, callback_data=f"country:{country}")]
        for country in locations_by_country.keys()
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_city_keyboard(country: str) -> InlineKeyboardMarkup:
    cities = locations_by_country.get(country, [])
    keyboard = [
        [InlineKeyboardButton(text=city, callback_data=f"city:{city}")]
        for city in cities
    ]
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back:country")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def get_date_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Сегодня", callback_data=f"{prefix}:today")],
        [InlineKeyboardButton(text="📆 Завтра", callback_data=f"{prefix}:tomorrow")],
        [InlineKeyboardButton(text="🗓 Выходные", callback_data=f"{prefix}:weekend")],
        [InlineKeyboardButton(text="📅 Этот месяц", callback_data=f"{prefix}:this_month")],
        [InlineKeyboardButton(text="📅 След. месяц", callback_data=f"{prefix}:next_month")],
        [InlineKeyboardButton(text="📌 Гибкие даты", callback_data=f"{prefix}:flexible")],
        [InlineKeyboardButton(text="✏ Ввести вручную", callback_data=f"{prefix}:manual")],
    ])

def get_purpose_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏖 Отдых", callback_data="purpose:отдых")],
        [InlineKeyboardButton(text="🧗 Приключения", callback_data="purpose:приключения")],
        [InlineKeyboardButton(text="🚚 Переезд", callback_data="purpose:переезд")],
        [InlineKeyboardButton(text="💼 Работа", callback_data="purpose:работа")],
        [InlineKeyboardButton(text="✏ Другое", callback_data="purpose:manual")]
    ])

def get_companions_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙋‍♀️ Только девушки", callback_data="companions:только девушки")],
        [InlineKeyboardButton(text="👫 Группа", callback_data="companions:группа")],
        [InlineKeyboardButton(text="👥 1–2 человека", callback_data="companions:1–2 человека")],
        [InlineKeyboardButton(text="❓ Не важно", callback_data="companions:не важно")],
        [InlineKeyboardButton(text="✏ Другое", callback_data="companions:manual")]
    ])

def get_search_filter_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Поиск по дате", callback_data="filter:date")],
        [InlineKeyboardButton(text="🎯 По цели поездки", callback_data="filter:purpose")],
        [InlineKeyboardButton(text="🧍 По спутникам", callback_data="filter:companions")],
        [InlineKeyboardButton(text="🌍 По направлению", callback_data="filter:location")],
        [InlineKeyboardButton(text="🎲 Случайные поездки", callback_data="filter:random")]
    ])
