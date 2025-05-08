from aiogram.fsm.state import StatesGroup, State

class FSMRegister(StatesGroup):
    contact = State()
    gender = State()
    birth_year = State()
    city = State()
    traveler_type = State()
    interests = State()
    bio = State()
    confirm = State()
