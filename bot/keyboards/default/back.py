from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def back_keyboard() -> ReplyKeyboardMarkup:
    """
    Create a keyboard with a back button.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back_button = KeyboardButton(text="🔙 Orqaga")
    keyboard.add(back_button)
    return keyboard