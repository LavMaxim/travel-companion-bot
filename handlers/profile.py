from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from database import save_deletion_feedback
from database import (
    get_user_by_id, get_trips_by_user,
    get_user_profile, update_user_field,
    delete_user_and_trips
)
from keyboards_main import menu_keyboard
from states.edit_profile import FSMEditProfile
from states.delete_profile import FSMDeleteProfile
from texts.trip import profile_template

router = Router()


# 🔗 /start profile_<id>
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


# 👤 Мой профиль
@router.message(F.text == "👤 Мой профиль")
async def show_profile(message: Message):
    user = get_user_profile(message.from_user.id)

    if not user:
        await message.answer("❗️Профиль не найден. Пожалуйста, пройди регистрацию через /register.")
        return

    text = (
        f"📇 <b>Твой профиль:</b>\n\n"
        f"👤 Имя: {user.get('full_name')}\n"
        f"🏙 Город: {user.get('city')}\n"
        f"🚶 Тип: {user.get('traveler_type')}\n"
        f"🎯 Интересы: {user.get('interests')}\n"
        f"📝 О себе: {user.get('bio')}\n"
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ Изменить профиль")],
            [KeyboardButton(text="🗑 Удалить профиль")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

    await message.answer(text, reply_markup=kb)


# ✏️ Изменение профиля
@router.message(F.text == "✏️ Изменить профиль")
async def choose_field_to_edit(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏙 Город"), KeyboardButton(text="🚶 Тип")],
            [KeyboardButton(text="🎯 Интересы"), KeyboardButton(text="📝 О себе")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Что вы хотите изменить?", reply_markup=kb)
    await state.set_state(FSMEditProfile.choosing_field)


@router.message(FSMEditProfile.choosing_field, F.text == "🔙 Назад")
async def back_to_profile_from_edit_field(message: Message, state: FSMContext):
    await state.clear()
    await show_profile(message)


@router.message(FSMEditProfile.choosing_field)
async def ask_for_new_value(message: Message, state: FSMContext):
    field_map = {
        "🏙 Город": "city",
        "🚶 Тип": "traveler_type",
        "🎯 Интересы": "interests",
        "📝 О себе": "bio"
    }

    field = field_map.get(message.text)
    if not field:
        await message.answer("Выберите пункт из предложенных.")
        return

    await state.update_data(field_to_edit=field)
    await message.answer("Введите новое значение:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMEditProfile.editing_value)


@router.message(FSMEditProfile.editing_value)
async def save_new_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data["field_to_edit"]
    new_value = message.text.strip()

    update_user_field(message.from_user.id, field, new_value)

    updated_user = get_user_profile(message.from_user.id)
    profile_text = (
        f"📇 <b>Твой обновлённый профиль:</b>\n\n"
        f"👤 Имя: {updated_user.get('full_name')}\n"
        f"🏙 Город: {updated_user.get('city')}\n"
        f"🚶 Тип: {updated_user.get('traveler_type')}\n"
        f"🎯 Интересы: {updated_user.get('interests')}\n"
        f"📝 О себе: {updated_user.get('bio')}"
    )

    await message.answer("✅ Данные обновлены!\n\n" + profile_text, reply_markup=menu_keyboard)
    await state.clear()


# 🗑 Удалить профиль
@router.message(F.text == "🗑 Удалить профиль")
async def confirm_delete(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]],
        resize_keyboard=True
    )
    await message.answer(
        "❗️Вы действительно хотите удалить профиль и все поездки?\n\n"
        "Это действие необратимо.",
        reply_markup=kb
    )
    await state.set_state(FSMDeleteProfile.confirm)


@router.message(FSMDeleteProfile.confirm, F.text == "❌ Нет")
async def cancel_delete(message: Message, state: FSMContext):
    await state.clear()
    await show_profile(message)


@router.message(FSMDeleteProfile.confirm, F.text == "✅ Да")
async def ask_reason_for_leaving(message: Message, state: FSMContext):
    delete_user_and_trips(message.from_user.id)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мало функций"), KeyboardButton(text="Сложный интерфейс")],
            [KeyboardButton(text="Мало людей"), KeyboardButton(text="Неактуально")],
            [KeyboardButton(text="Потерял интерес"), KeyboardButton(text="📝 Другое")],
            [KeyboardButton(text="Просто тестировал")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "😔 Очень жаль, что вы уходите.\n"
        "Помогите нам стать лучше — выберите причину:",
        reply_markup=kb
    )
    await state.set_state(FSMDeleteProfile.feedback_reason)


@router.message(FSMDeleteProfile.feedback_reason, F.text == "📝 Другое")
async def request_custom_reason(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите причину (до 200 символов):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMDeleteProfile.custom_reason)


@router.message(FSMDeleteProfile.custom_reason)
async def handle_custom_reason(message: Message, state: FSMContext):
    reason = message.text.strip()[:200]
    save_deletion_feedback(message.from_user.id, message.from_user.username or "", reason)
    print(f"[FEEDBACK] Пользователь удалил профиль. Причина (другое): {reason}")
    await message.answer("Спасибо, что поделились! Будем рады увидеть вас снова 🙏", reply_markup=menu_keyboard)
    await state.clear()


@router.message(FSMDeleteProfile.feedback_reason)
async def thank_after_standard_reason(message: Message, state: FSMContext):
    reason = message.text.strip()
    save_deletion_feedback(message.from_user.id, message.from_user.username or "", reason)
    await message.answer("Спасибо за обратную связь 🙏 Будем рады увидеть вас снова!", reply_markup=menu_keyboard)
    await state.clear()


# 🔙 Назад в главное меню
@router.message(F.text == "🔙 Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📍 Главное меню", reply_markup=menu_keyboard)
