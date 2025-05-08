# texts/trip.py

location_hint = (
    "🏙 Введите город/страну, куда вы хотите поехать:\n"
    "<i>Допустимы только буквы, пробелы, дефисы. Пример: Санкт-Петербург</i>"
)

date_format_error = (
    "⚠ Неверный формат. Введите дату в формате <b>ДД.ММ.ГГГГ</b>.\n"
    "Пример: 12.08.2025"
)
description_too_long = "⚠ Описание слишком длинное. Укоротите до 300 символов."
date_from_hint = "📅 Введите дату начала поездки (например, 12.08.2025):"
date_to_hint = "📅 Теперь введите дату окончания поездки:"
purpose_hint = "🎯 Укажите цель поездки (например: отдых, приключения, работа и т.д.):"
purpose_manual_hint = "✏ Введите свою цель поездки:"
companions_hint = "🧍 Кого вы ищете в попутчики?"
companions_manual_hint = "✏ Введите, кого вы ищете в попутчики:"
description_hint = (
    "📝 Добавьте краткое описание (до 300 символов):\n"
    "<i>Например: немного о себе, Instagram, условия поездки, наличие машины и т.п.</i>"
)

profile_template = """👤 Профиль {first_name} {last_name} (@{username})

📌 Поездки:
{trips}
"""

trip_line_template = """— {location} ({date_from} — {date_to}): {purpose}, {companions}"""


# 💬 Универсальный формат карточки поездки
def format_trip_card(trip, author: dict=None, is_own: bool=False) -> str:
    if isinstance(trip, dict):
        # trip — это dict из create_trip, раскладываем по ключам
        rowid       = trip.get("rowid")       # если у вас есть ID
        user_id     = trip.get("user_id")
        username    = trip.get("username")
        country     = trip.get("country")
        location    = trip.get("location")
        date_from   = trip.get("date_from")
        date_to     = trip.get("date_to")
        purpose     = trip.get("purpose")
        companions  = trip.get("companions")
        description = trip.get("description")
        insert_dttm = trip.get("insert_dttm", "")  # или datetime.now()
    else:
        # старый вариант — кортеж
        (
            rowid, user_id, username, country, location,
            date_from, date_to, purpose, companions,
            description, insert_dttm
        ) = trip

    # далее общий код сборки текста…
    username_display = f"@{username}" if username else "<i>аноним</i>"

    text = (
        f"🌍 <b>Страна:</b> {country or '—'}\n"
        f"🌍 <b>Место:</b> {location or '—'}\n"
        f"📅 <b>С:</b> {date_from or '—'}\n"
        f"📅 <b>По:</b> {date_to or '—'}\n"
        f"🎯 <b>Цель:</b> {purpose or '—'}\n"
        f"🧍 <b>Спутники:</b> {companions or '—'}\n"
        f"📝 <b>Описание:</b> {description or '—'}\n"
        f"⏱️ <b>Добавлено:</b> {insert_dttm or '—'}\n"
    )

    if not is_own and author:
        text += "\n"
        text += f"👤 <b>{author.get('full_name', '—')}</b> "
        if author.get("username"):
            text += f"(@{author['username']})\n"
        text += f"🏙 {author.get('city', '—')}\n"
        text += f"🚶 {author.get('traveler_type', '—')}\n"
        text += f"🎯 Интересы: {author.get('interests', '—')}\n"
        text += f"📝 О себе: {author.get('bio', '—')}"

    return text



def render_profile_template(user: dict, trips: list) -> str:
    def trip_to_dict(trip):
        if isinstance(trip, dict):
            return trip
        return {
            "location": trip[4],
            "date_from": trip[5],
            "date_to": trip[6],
            "purpose": trip[7],
            "companions": trip[8]
        }

    if trips:
        trips_text = "\n".join([
            trip_line_template.format(**trip_to_dict(trip)) for trip in trips
        ])
    else:
        trips_text = "Нет активных поездок."

    return profile_template.format(
        first_name=user.get("first_name", ""),
        last_name=user.get("last_name", ""),
        username=user.get("username", "без username"),
        trips=trips_text
    )

