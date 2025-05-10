from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from bot.loader import dp, db
from bot.keyboards.default import main_kb
from bot.keyboards.inline.send_task import send_task_keyboard
from botapp.tasks import update_google_sheet
from aiogram.dispatcher import FSMContext


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()

    user, created = await db.get_or_create_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        language_code=message.from_user.language_code
    )
    
    # Check if the user is blocked
    if user['is_blocked']:
        await message.answer("Siz bloklangansiz. Iltimos, admin bilan bog'laning.")
        return

    # Check if the user have not completed task
    task = await db.get_user_task(user['user_id'])
    if task:
        if task['status'] == 'pending':
            await message.answer(
                "Sizda hali topshiriq mavjud. Iltimos, topshirig'ingizni bajaring.\n" \
                "Sizga topshirilgan topshiriq:\n\n" \
                f"{task['task']}\n\n" \
                f"Muddati: {task['deadline']}\n\n" \
                "Iltimos, topshirig'ingizni bajaring.",
                reply_markup=send_task_keyboard(task_id=task['id']) # topshiriqni ko'rish uchun kerakli tugma
            )
            return
        elif task['status'] == 'sent':
            await message.answer(
                "Siz topshiriqni yuborgansiz. Iltimos javobini kuting.",
                reply_markup=types.ReplyKeyboardRemove() # topshiriqni ko'rish uchun kerakli tugma
            )
            return


    vacancies = await db.get_active_vacancies()
    # register user
    
    update_google_sheet.delay(
            user_id=user['user_id'],
            step="start",
            data=message.from_user.id
        )

    if vacancies:
        active_vacancies = "\n".join([f"• {vacancy['name']}" for vacancy in vacancies])
        await message.answer(
            f"Assalomu alaykum!\n"
            f"Hozirda bizda quyidagi bo'sh ish o'rinlari mavjud:\n"
            f"{active_vacancies}",
            reply_markup=main_kb
        )
    else:
        await message.answer("Hozirda bo'sh ish o'rinlari mavjud emas.\n")



