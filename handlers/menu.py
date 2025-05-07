from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from keyboards_main import menu_keyboard
from handlers.create_trip import start_trip_creation
from handlers.mytrips import show_my_trips
from keyboards.trip import get_search_filter_keyboard
from database import is_user_registered
from handlers.profile import show_profile
from handlers.register import register_start
from texts.trip import format_trip_card
from aiogram import Router, types
from logger import get_logger

logger = get_logger(__name__)
router = Router()

@router.message(Command("start"))
async def handle_start(message: Message):
    await message.answer(
        "Привет! 👋 Я помогу тебе найти попутчиков ✈️",
        reply_markup=menu_keyboard
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
        await register_start(message, state)  # 👉 сразу уводим в регистрацию
        return
    await show_profile(message)
