from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.register import FSMRegister
from database import save_user
from keyboards_main import get_menu_keyboard
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(F.text == "/register")
async def register_start(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Поделитесь своей карточкой Telegram:", reply_markup=kb)
    await state.set_state(FSMRegister.contact)


@router.message(F.contact)
async def save_contact(message: Message, state: FSMContext):
    contact = message.contact
    await state.update_data(
        telegram_id=contact.user_id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        contact_phone=contact.phone_number
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужчина")],
            [KeyboardButton(text="Женщина")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
        )
    await message.answer("🧬 Укажите ваш пол:", reply_markup=kb)
    await state.set_state(FSMRegister.gender)

@router.message(FSMRegister.gender)
async def get_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("📅 Введите ваш год рождения (например, 1992):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMRegister.birth_year)


@router.message(FSMRegister.birth_year)
async def get_birth_year(message: Message, state: FSMContext):
    year = message.text.strip()
    if not year.isdigit() or not (1900 <= int(year) <= 2025):
        await message.answer("⚠ Пожалуйста, введите корректный год (например, 1990).")
        return

    await state.update_data(birth_year=int(year))
    await message.answer("🌆 В каком городе вы живёте?")
    await state.set_state(FSMRegister.city)


@router.message(FSMRegister.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Соло")], [KeyboardButton(text="Группа")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Вы путешествуете один или с группой?", reply_markup=kb)
    await state.set_state(FSMRegister.traveler_type)


@router.message(FSMRegister.traveler_type)
async def get_traveler_type(message: Message, state: FSMContext):
    await state.update_data(traveler_type=message.text)
    await message.answer(
        "Какие интересы вам ближе?\n\nПример: прогулки, экскурсии, тусовки, гастротуры",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FSMRegister.interests)


@router.message(FSMRegister.interests)
async def get_interests(message: Message, state: FSMContext):
    await state.update_data(interests=[i.strip() for i in message.text.split(",")])
    await message.answer("Расскажите немного о себе:")
    await state.set_state(FSMRegister.bio)


@router.message(FSMRegister.bio)
async def get_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    data = await state.get_data()

    text = (
        f"📋 <b>Проверьте анкету:</b>\n"
        f"👤 Имя: <b>{data.get('full_name')}</b>\n"
        f"🧬 Пол: <b>{data.get('gender')}</b>\n"
        f"📅 Год рождения: <b>{data.get('birth_year')}</b>\n"
        f"📱 Телефон: <b>{data.get('contact_phone')}</b>\n"
        f"🏙 Город: <b>{data.get('city')}</b>\n"
        f"🚶 Тип: <b>{data.get('traveler_type')}</b>\n"
        f"🎯 Интересы: <b>{', '.join(data.get('interests', []))}</b>\n"
        f"📝 О себе: <b>{data.get('bio')}</b>\n\n"
        f"<b>✅ Всё верно?</b>"
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Подтвердить")],
            [KeyboardButton(text="🔁 Изменить")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(text, reply_markup=kb)
    await state.set_state(FSMRegister.confirm)


@router.message(FSMRegister.confirm, F.text.lower().in_(["✅ подтвердить", "подтвердить", "да", "yes"]))
async def confirm_registration(message: Message, state: FSMContext):
    data = await state.get_data()

    user_data = {
        "telegram_id": data.get("telegram_id"),
        "username": data.get("username"),
        "full_name": data.get("full_name"),
        "contact_phone": data.get("contact_phone"),
        "city": data.get("city"),
        "traveler_type": data.get("traveler_type"),
        "interests": data.get("interests", []),
        "bio": data.get("bio"),
        "gender": data.get("gender"),
        "birth_year": data.get("birth_year"),
    }

    save_user(user_data)

    await message.answer(
        "✅ Спасибо за регистрацию!\n\nТеперь ты можешь:\n— ➕ создать свою поездку\n— 🔎 найти компанию для путешествия\n— 🧳 просмотреть свои поездки",
        reply_markup=get_menu_keyboard(message.from_user.id)
    )
    await state.clear()

@router.message(FSMRegister.confirm, F.text.lower().in_(["🔁 изменить", "изменить", "нет", "повторить"]))
async def restart_registration(message: Message, state: FSMContext):
    await state.clear()
    await register_start(message, state)


@router.message(FSMRegister.confirm)
async def fallback_confirmation(message: Message):
    await message.answer("Пожалуйста, нажмите кнопку '✅ Подтвердить' или введите 'Да'.")

