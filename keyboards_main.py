from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command 
from handlers.create_trip import start_trip_creation
from handlers.mytrips import show_my_trips
from aiogram.types import (
    CallbackGame,
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonPollType,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
    LoginUrl,
    ReplyKeyboardMarkup,
    SwitchInlineQueryChosenChat,
    WebAppInfo,
)
from database import count_unread_notifications

def get_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    unread_count = count_unread_notifications(user_id)
    notif_label = f"🔔 Уведомления ({unread_count})" if unread_count > 0 else "🔔 Уведомления"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Создать поездку")],
            [KeyboardButton(text="🔎 Поиск"), KeyboardButton(text="🧳 Мои поездки")],
            [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text=notif_label)],
            [KeyboardButton(text="🆘 Помощь")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие 👇"
    )