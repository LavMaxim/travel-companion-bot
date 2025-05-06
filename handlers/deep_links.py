from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

from texts.trip import profile_template, trip_line_template
from database import get_user_by_id, get_trips_by_user
from texts.trip import format_trip_card

router = Router()

@router.message(CommandStart(deep_link=True))
async def handle_deep_link(message: Message, command: CommandObject):
    if command.args and command.args.startswith("profile_"):
        user_id = command.args.split("_")[1]
        await show_user_profile(message, user_id)
    else:
        await message.answer("Добро пожаловать в бота! 🎒")

async def show_user_profile(message: Message, user_id: str):
    user = get_user_by_id(int(user_id))
    trips = get_trips_by_user(int(user_id))

    if not user:
        await message.answer("❌ Пользователь не найден.")
        return

    if trips:
        trips_text = "\n".join(
            [trip_line_template.format(**t) for t in trips]
        )
    else:
        trips_text = "Нет активных поездок."

    text = profile_template.format(
        first_name=user.get("first_name", ""),
        last_name=user.get("last_name", ""),
        username=user.get("username", "без username"),
        trips=trips_text
    )

    await message.answer(text)
