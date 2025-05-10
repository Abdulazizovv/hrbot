from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

send_task_callback = CallbackData("send_task", "task_id")


def send_task_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard for sending a task.
    :param task_id: The ID of the task to be sent.
    :return: InlineKeyboardMarkup object with the send task button.
    """
    keyboard = InlineKeyboardMarkup()
    send_task_button = InlineKeyboardButton(
        text="Topshiriqni yuborish",
        callback_data=send_task_callback.new(task_id=task_id)
    )
    keyboard.add(send_task_button)
    return keyboard