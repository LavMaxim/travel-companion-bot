from aiogram.fsm.state import State, StatesGroup

class FSMRegister(StatesGroup):
    contact = State()
    full_name = State()
    city = State()
    traveler_type = State()
    interests = State()
    bio = State()
    confirm = State()