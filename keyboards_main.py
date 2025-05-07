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

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Создать поездку")],
        [KeyboardButton(text="🔎 Поиск"), KeyboardButton(text="🧳 Мои поездки")],
        [KeyboardButton(text="👤 Мой профиль")],  # ← добавили запятую в конце списка
        [KeyboardButton(text="🆘 Помощь")],      # ← теперь это отдельный вложенный список
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие 👇"
)

