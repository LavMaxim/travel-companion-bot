from aiogram.fsm.state import StatesGroup, State

class FSMTrip(StatesGroup):
    country = State()
    city = State()
    date_from = State()
    date_to = State()
    purpose = State()
    companions = State()
    description = State()
