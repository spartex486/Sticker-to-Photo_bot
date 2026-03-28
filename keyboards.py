from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="Фото в Стикер")],
        [KeyboardButton(text="Стикер в фото")]
    ],
    resize_keyboard=True
)
