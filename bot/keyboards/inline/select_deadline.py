from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

user_deadline_callback = CallbackData("user_deadline", "action", "deadline", "task_id")

deadlines = ["1 kun", "2 kun", "3 kun", "4 kun"]

def get_deadline_keyboard(task_id) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for selecting a deadline.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for deadline in deadlines:
        button = InlineKeyboardButton(
            text=deadline,
            callback_data=user_deadline_callback.new(action="select", deadline=deadline, task_id=task_id)
        )
        keyboard.insert(button)

    
    return keyboard