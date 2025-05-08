from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.deep_linking import decode_payload

from handlers.create_trip import start_trip_creation
from handlers.mytrips import show_my_trips
from handlers.profile import show_profile
from handlers.register import register_start
from handlers.help import cmd_help
from handlers.notifications import notification_filter_keyboard

from keyboards.trip import get_search_filter_keyboard
from database import (
    is_user_registered,
    get_user_by_id,
    get_trips_by_user,
    get_trip_by_id,
    get_unread_notifications,
    count_unread_notifications
)
from texts.trip import format_trip_card, render_profile_template

from logger import get_logger

logger = get_logger(__name__)
router = Router()


# 📋 Главное меню с динамическим счётчиком
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


# 🚀 /start с диплинком
@router.message(CommandStart(deep_link=True))
async def handle_start_with_payload(message: Message, command: CommandObject):
    if command.args:
        payload = decode_payload(command.args)

        if payload.startswith("profile_"):
            user_id = payload.split("_")[1]
            user_data = get_user_by_id(user_id)
            if not user_data:
                await message.answer("Профиль не найден.")
                return

            trips = get_trips_by_user(user_id)
            text = render_profile_template(user_data, trips)
            await message.answer(text, disable_web_page_preview=True)
            return

        elif payload.startswith("trip_"):
            trip_id = payload.split("_")[1]
            trip = get_trip_by_id(trip_id)
            if not trip:
                await message.answer("Поездка не найдена.")
                return

            author = get_user_by_id(trip[1])
            text = format_trip_card(trip, author, is_own=False)
            await message.answer(text, disable_web_page_preview=True)
            return

    await message.answer(
        "Привет! 👋 Я помогу тебе найти попутчиков ✈️",
        reply_markup=get_menu_keyboard(message.from_user.id)
    )


# 🧭 /start без аргументов
@router.message(CommandStart())
async def handle_plain_start(message: Message):
    await message.answer(
        "Привет! 👋 Я помогу тебе найти попутчиков ✈️",
        reply_markup=get_menu_keyboard(message.from_user.id)
    )


@router.message(F.text == "➕ Создать поездку")
async def handle_create_button(message: Message, state: FSMContext):
    if not is_user_registered(message.from_user.id):
        await message.answer("❗️Чтобы пользоваться ботом, нужно пройти регистрацию.\nНажми /register.")
        return
    await start_trip_creation(message, state)


@router.message(F.text == "🧳 Мои поездки")
async def handle_mytrips_button(message: Message):
    if not is_user_registered(message.from_user.id):
        await message.answer("❗️Сначала пройди регистрацию, чтобы видеть свои поездки.\nНажми /register.")
        return
    await show_my_trips(message)


@router.message(F.text == "🔎 Поиск")
async def handle_find_button(message: Message):
    if not is_user_registered(message.from_user.id):
        await message.answer("❗️Поиск доступен только после регистрации.\nНажми /register.")
        return
    await message.answer(
        "Выберите параметр для поиска поездки:",
        reply_markup=get_search_filter_keyboard()
    )


@router.message(F.text == "👤 Мой профиль")
async def handle_profile(message: Message, state: FSMContext):
    if not is_user_registered(message.from_user.id):
        await message.answer("❗️Чтобы пользоваться ботом, нужно пройти регистрацию.\nНачнем прямо сейчас ⬇️")
        await register_start(message, state)
        return
    await show_profile(message)


@router.message(F.text == "🆘 Помощь")
async def goto_help(message: Message, state: FSMContext):
    await cmd_help(message)


# 📬 Просмотр уведомлений
@router.message(F.text.startswith("🔔 Уведомления"))
async def show_notifications(message: Message):
    user_id = message.from_user.id
    notifications = get_unread_notifications(user_id)

    if not notifications:
        await message.answer(
            "🔕 У тебя нет новых уведомлений.",
            reply_markup=notification_filter_keyboard()
        )
        return

    for notif in notifications:
        notif_id, notif_type, payload, created_at = notif

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Прочитано", callback_data=f"notif_read:{notif_id}")]
        ])

        await message.answer(
            f"📬 <b>{created_at[:16]}</b>\n\n{payload}",
            reply_markup=kb,
            parse_mode="HTML"
        )

    await message.answer("🔎 Фильтр уведомлений:", reply_markup=notification_filter_keyboard())
