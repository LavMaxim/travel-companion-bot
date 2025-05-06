from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from keyboards.trip import get_search_filter_keyboard
from texts.trip import format_trip_card


router = Router()


@router.message(Command("find"))
async def show_find_menu(message: Message):
    await message.answer(
        "Выберите параметр для поиска поездки:",
        reply_markup=get_search_filter_keyboard()
    )

