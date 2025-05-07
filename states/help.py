from aiogram.fsm.state import State, StatesGroup

class HelpStates(StatesGroup):
    instruction = State()   
    choose_type = State()
    collect     = State()