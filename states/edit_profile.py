from aiogram.fsm.state import StatesGroup, State

class FSMEditProfile(StatesGroup):
    choosing_field = State()
    editing_value = State()
