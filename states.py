from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class Form(StatesGroup):
    waiting_for_photo = State()   # Состояние ожидания фото
    waiting_for_sticker = State() # Состояние ожидания стикера