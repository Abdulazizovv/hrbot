from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def vacancies_keyboard(vacancies) -> ReplyKeyboardMarkup:
    """
    Create a keyboard for vacancies.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = []
    
    for vacancy in vacancies:
        button = KeyboardButton(vacancy['name'])
        buttons.append(button)
    
    keyboard.add(*buttons)
    back_button = KeyboardButton(text="🔙 Orqaga")
    keyboard.add(back_button)
    return keyboard