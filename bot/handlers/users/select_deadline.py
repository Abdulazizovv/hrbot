from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.loader import dp, db
from bot.keyboards.inline.select_deadline import user_deadline_callback
from bot.keyboards.inline.send_task import send_task_keyboard
from botapp.tasks import update_google_sheet
from django.utils import timezone
from datetime import timedelta


@dp.callback_query_handler(user_deadline_callback.filter(action="select"))
async def select_deadline(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Handles the selection of a deadline for a task.
    """
    await call.answer(cache_time=60)
    
    deadline = callback_data.get("deadline")
    task_id = callback_data.get("task_id")
    
    # Update the task in the database with the selected deadline
    user_task = await db.get_user_task_by_id(task_id)
    if user_task:
        await db.update_user_task(task_id, 'user_deadline', deadline)
        days = int(deadline.split()[0]  if deadline.split()[0].isdigit() else 1)
        await db.update_user_task(task_id, 'deadline', timezone.now() + timedelta(days=days))
        
        update_google_sheet.apply_async(
                kwargs={
                    'user_id': user_task['user'],
                    'step': 'deadline',
                    'data': user_task['deadline']
                },
                countdown=3  # 3 soniyadan keyin bajariladi
            )
        
        update_google_sheet.delay(
            user_id=user_task['user'],
            step='select_deadline',
            data=deadline,
        )
        await call.message.edit_text(
            text=f"Vazifa uchun muddatni {deadline} qilib belgiladingiz.\n\n"
                 f"Vazifa:\n\n{user_task['task']}\n\n"
                 f"Omad tilaymiz!",
            reply_markup=send_task_keyboard(user_task['id']),
        )
        await state.finish()
        return
    
    await call.message.edit_text(
        text="Vazifa topilmadi. Iltimos, qayta urinib ko'ring.",
        reply_markup=None,
    )