from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from keyboards_main import menu_keyboard
from handlers.create_trip import start_trip_creation
from handlers.mytrips import show_my_trips
from keyboards.trip import get_search_filter_keyboard
router = Router()

@router.message(Command("start"))
async def handle_start(message: Message):
    await message.answer(
        "Привет! 👋 Я помогу тебе найти попутчиков ✈️",
        reply_markup=menu_keyboard
    )

@router.message(F.text == "➕ Создать поездку")
async def handle_create_button(message: Message, state: FSMContext):
    await start_trip_creation(message, state)

@router.message(F.text == "🧳 Мои поездки")
async def handle_mytrips_button(message: Message):
    await show_my_trips(message)

@router.message(F.text == "🔎 Поиск")
async def handle_find_button(message: Message):
    await message.answer(
        "Выберите параметр для поиска поездки:",
        reply_markup=get_search_filter_keyboard()
    )