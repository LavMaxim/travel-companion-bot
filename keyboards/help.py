from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts.help import faq_category_general_questions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts.help import faq_category_general_questions

def help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❓ FAQ",            callback_data="help:faq")],
            [InlineKeyboardButton(text="📘 Инструкции",     callback_data="help:instr")],
            [InlineKeyboardButton(text="✉️ Обратная связь", callback_data="help:feedback")],
        ]
    )

def faq_categories_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=cat.title(), callback_data=f"faq:category:{cat}")]
        for cat in faq_category_general_questions.keys()
    ] + [
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="help:menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def faq_questions_kb(category: str) -> InlineKeyboardMarkup:
    qs = faq_category_general_questions.get(category, [])
    buttons = [
        [InlineKeyboardButton(text=q, callback_data=f"faq:question:{category}:{idx}")]
        for idx, q in enumerate(qs)
    ] + [
        [InlineKeyboardButton(text="◀️ Назад", callback_data="help:faq")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="help:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def faq_answers_kb(category: str) -> InlineKeyboardMarkup:
    # Кнопка «Назад» теперь возвращает к списку вопросов именно этой категории
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"faq:category:{category}")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="help:menu")],
        ]
    )

def instruction_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛠 Как создать поездку", callback_data="instr:create:0")],
            [InlineKeyboardButton(text="🤝 Как присоединиться",   callback_data="instr:join:0")],
            [InlineKeyboardButton(text="📋 Где мои поездки",      callback_data="instr:view:0")],
            [InlineKeyboardButton(text="🔍 Как искать поездки",   callback_data="instr:search:0")],
            [InlineKeyboardButton(text="🏠 Главное меню",         callback_data="help:menu")],
        ]
    )

def instruction_kb(topic: str, idx: int, total: int) -> InlineKeyboardMarkup:
    buttons = []
    if idx + 1 < total:
        buttons.append([
            InlineKeyboardButton(
                text=f"Следующий ({idx+1}/{total}) ▶️",
                callback_data=f"instr:{topic}:{idx+1}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="help:menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def feedback_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❓ Вопрос", callback_data="fb:type:question")],
            [InlineKeyboardButton(text="🐞 Баг",    callback_data="fb:type:bug")],
            [InlineKeyboardButton(text="💡 Идея",   callback_data="fb:type:idea")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="fb:cancel")],
        ]
    )

def feedback_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="fb:cancel")],
        ]
    )
