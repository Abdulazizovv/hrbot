from aiogram import types
from bot.loader import dp, db
from bot.keyboards.inline.send_task import send_task_callback
from aiogram.dispatcher import FSMContext
from botapp.tasks import update_google_sheet
from django.utils import timezone
import re
import aiohttp


GITHUB_REPO_PATTERN = r'^https://github\.com/[\w\-]+/[\w\-]+/?$'

@dp.callback_query_handler(send_task_callback.filter(), state='*')
async def handle_send_task(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Handle the send task callback.
    :param callback_query: The callback query object.
    :param callback_data: The data from the callback query.
    """
    await call.answer()
    task_id = int(callback_data['task_id'])
    task = await db.get_user_task_by_id(task_id)
    if task:
        if task['status'] == 'completed':
            await call.message.answer("Siz ushbu topshiriqni yuborgansiz.")
            return
        
        # if not task['is_valid']:
        #     await call.message.answer("Topshiriqni yuborish muddati tugagan.")
        #     return

        if task['status'] == 'pending':
            await state.update_data(task_id=task_id)
            await call.message.answer("Topshiriq uchun github link yuboring.")
            await state.set_state('send_task_link')
            return
    else:
        await call.message.answer("Topshiriq topilmadi.")
        return
    

@dp.message_handler(state='send_task_link')
async def handle_send_task_link(message: types.Message, state: FSMContext):
    """
    Handle the send task link message.
    :param message: The message object.
    :param state: The FSM context.
    """
    link = message.text.strip()

    if not re.match(GITHUB_REPO_PATTERN, link):
        await message.answer("❌ Iltimos, to'g'ri GitHub havolasini kiriting. Masalan: https://github.com/username/repo")
        return

    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(link) as response:
                if response.status != 200:
                    await message.answer("❌ Ushbu GitHub repozitoriyasi mavjud emas yoki yopiq (private).\n"
                                         "Iltimos, ochiq (public) repozitoriya havolasini yuboring.")
                    return
        except Exception as e:
            await message.answer("❌ Havolani tekshirishda xatolik yuz berdi.\nKeyinroq qaytadan urinib ko'ring.")
            return

    data = await state.get_data()
    task_id = data.get('task_id')
    if task_id:
        task = await db.get_user_task_by_id(task_id)
        sent_task = await db.add_submission(task['id'], link)
        
        if task and sent_task:
            update_google_sheet.delay(
                user_id=message.from_user.id,
                step='task_link',
                data=link,
            )
            await db.change_user_task_status(message.from_user.id, task_id, 'sent')
            await db.update_user_task(task_id, 'status', 'sent')
            await message.answer("Topshiriq muvaffaqiyatli yuborildi.\n"
                                 "Siz bilan bog'lanamiz.\n"
                                 "Rahmat!")
            await db.update_user_task(user_task_id=task['id'], field='status', value='sent')
            await db.update_user_task(user_task_id=task['id'], field='finished_at', value=timezone.localtime())
            update_google_sheet.delay(
                user_id=message.from_user.id,
                step='task_end',
                data=timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
            )
            update_google_sheet.delay(
                user_id=message.from_user.id,
                step='status',
                data='Vazifa topshirildi',
            )
            await state.finish()
            return
    else:
        await message.answer("Topshiriq topilmadi.\nIltimos, keyinroq qaytadan urinib ko'ring.")
        await state.finish()
        return