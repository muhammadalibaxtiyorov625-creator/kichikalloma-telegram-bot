from aiogram.fsm.state import State, StatesGroup

class SupportState(StatesGroup):
    waiting_for_help_message = State()
