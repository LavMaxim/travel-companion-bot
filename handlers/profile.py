from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

from database import get_user_by_id, get_trips_by_user
from texts.trip import profile_template

router = Router()

@router.message(CommandStart(deep_link=True))
async def handle_deep_link_profile(message: Message, command: CommandObject):
    if command.args and command.args.startswith("profile_"):
        user_id = command.args.split("_")[1]

        user_data = get_user_by_id(user_id)
        if not user_data:
            await message.answer("Профиль не найден.")
            return

        trips = get_trips_by_user(user_id)

        text = profile_template(user_data, trips)
        await message.answer(text, disable_web_page_preview=True)
    else:
        await message.answer("Добро пожаловать в бота!")
