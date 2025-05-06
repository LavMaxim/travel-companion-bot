from aiogram.fsm.state import StatesGroup, State

class FSMDeleteProfile(StatesGroup):
    confirm = State()
    feedback_reason = State()
    custom_reason = State() 
