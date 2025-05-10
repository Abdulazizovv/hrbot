from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.loader import dp, db
from botapp.tasks import update_google_sheet, send_notification


@dp.callback_query_handler(text_contains='confirm_task')
async def confirm_task(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    task_id = call.data.split('_')[-1]
    user_task = await db.get_user_task_by_id(task_id)
    if user_task:
        if user_task['status'] in ['approved', 'rejected']:
            await call.message.edit_reply_markup(
                reply_markup=None
            )
            await call.message.reply(
                text="Bu vazifa allaqachon tasdiqlangan yoki rad etilgan.",
                reply_markup=None
            )
            return
        await db.update_user_task(task_id, 'status', 'approved')
        update_google_sheet.delay(
            user_id=user_task['user'],
            step='status',
            data='Tasdiqlandi',
        )
        await call.message.edit_reply_markup(
            reply_markup=None
        )
        await call.message.reply(
            text="Tasdiqlandi"
        )
        # send_notification.delay(
        #     user_id=user_task['user'],
        #     text=(
        #         f"✅ Sizning vazifangiz tasdiqlandi:\n\n"
        #         f"Yaqin orada siz bilan bog'lanamiz.\n"
        #     )
        # )
    else:
        await call.message.edit_reply_markup(
            reply_markup=None
        )
        await call.message.reply(
            text="Task not found or already confirmed.",
            reply_markup=None
        )