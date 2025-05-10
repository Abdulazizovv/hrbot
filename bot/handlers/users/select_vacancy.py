from aiogram import types
from bot.loader import dp, db
from bot.keyboards.default.vacancies import vacancies_keyboard
from bot.keyboards.default.main_kb import main_kb
from bot.keyboards.default.back import back_keyboard
from bot.keyboards.inline.send_task import send_task_keyboard
from bot.keyboards.inline.select_deadline import get_deadline_keyboard
from aiogram.dispatcher import FSMContext
from botapp.tasks import update_google_sheet, send_application_to_admins
from django.utils import timezone
import logging
from celery import chain


# @dp.message_handler(text='🔙 Orqaga', state="*")
# async def back_to_section(message: types.Message, state: FSMContext):
#     """
#     Handle the back button to return to the main menu.
#     """
#     data = await state.get_data()
#     step = data.get("step")


@dp.message_handler(text='🧾 Ariza qoldirish')
async def show_vacancies(message: types.Message, state: FSMContext):
    """
    Show the list of vacancies to the user.
    """
    vacancies = await db.get_active_vacancies()

    if vacancies:
        await message.answer(
            "Tanlang 👇\n",
            reply_markup=vacancies_keyboard(vacancies)
        )
        await state.set_state("vacancy_selection")
        return
    else:
        await message.answer("Hozirda bo'sh ish o'rinlari mavjud emas.\n", reply_markup=types.ReplyKeyboardRemove())
        return
    

@dp.message_handler(state="vacancy_selection")
async def handle_vacancy_selection(message: types.Message, state: FSMContext):
    """
    Handle the user's selection of a vacancy.
    """
    if message.text == "🔙 Orqaga":
        await message.answer("Bosh sahifa", reply_markup=main_kb)
        await state.finish()
        return
    
    selected_vacancy = message.text
    # Check if the selected vacancy is valid
    vacancies = await db.get_active_vacancies()
    if selected_vacancy not in [vacancy['name'] for vacancy in vacancies]:
        await message.answer("Iltimos, ro'yxatdan birini tanlang.", reply_markup=vacancies_keyboard(vacancies))
        await state.set_state("vacancy_selection")
        return
    update_google_sheet.delay(
        user_id=message.from_user.id,
        step="vacancy",
        data=selected_vacancy
    )
    update_google_sheet.delay(
        user_id=message.from_user.id,
        step="status",
        data="Yangi"
    )

    update_google_sheet.delay(
        user_id=message.from_user.id,
        step="timestamp",
        data=timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    await db.save_application_partially(
        user_id=message.from_user.id,
        part="vacancy",
        data=selected_vacancy
    )

    await state.update_data(selected_vacancy=selected_vacancy)
    await message.answer(f"Siz tanlagan ish o'rni: {selected_vacancy}\n"
                         f"Ismingizni kiriting.", reply_markup=back_keyboard())
    await state.set_state("name_input")
    await state.set_state("name_input")

@dp.message_handler(state="name_input")
async def handle_name_input(message: types.Message, state: FSMContext):
    """
    Handle the user's input of their name.
    """

    if message.text == "🔙 Orqaga":
        vacancies = await db.get_active_vacancies()

        if vacancies:
            await message.answer(
                "Tanlang 👇\n",
                reply_markup=vacancies_keyboard(vacancies)
            )
            await state.set_state("vacancy_selection")
            return
        else:
            await message.answer("Hozirda bo'sh ish o'rinlari mavjud emas.\n", reply_markup=types.ReplyKeyboardRemove())
            return

    user_data = await state.get_data()
    selected_vacancy = user_data.get("selected_vacancy")
    name = message.text
    await state.update_data(name=name)

    # Save the application to the database
    await db.save_application_partially(
        user_id=message.from_user.id,
        part="name",
        data=name
    )
    update_google_sheet.delay(
        user_id=message.from_user.id,
        step="name",
        data=name
    )

    await message.answer("Telefon raqamingizni yuboring 👇", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True),
            ],
            [
                types.KeyboardButton(text="🔙 Orqaga"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ))

    await state.update_data(step="phone_input")

    await state.set_state("phone_input")

@dp.message_handler(state="phone_input", content_types=types.ContentType.TEXT)
async def handle_phone_input_text(message: types.Message, state: FSMContext):
    """
    Handle the user's input of their phone number.
    """
    if message.text == "🔙 Orqaga":
        vacancies = await db.get_active_vacancies()

        if vacancies:
            await message.answer(
                "Tanlang 👇\n",
                reply_markup=vacancies_keyboard(vacancies)
            )
            await state.set_state("vacancy_selection")
            return
        else:
            await message.answer("Hozirda bo'sh ish o'rinlari mavjud emas.\n", reply_markup=types.ReplyKeyboardRemove())
            return

    await message.answer("Iltimos, telefon raqamingizni yuboring.", reply_markup=back_keyboard())
    await state.set_state("phone_input")


@dp.message_handler(content_types=types.ContentType.CONTACT, state="phone_input")
async def handle_phone_input(message: types.Message, state: FSMContext):
    """
    Handle the user's input of their phone number.
    """
    user_data = await state.get_data()
    selected_vacancy = user_data.get("selected_vacancy")
    phone_number = message.contact.phone_number

    # Save the application to the database
    await db.save_application_partially(
        user_id=message.from_user.id,
        part="phone",
        data=phone_number
    )
    update_google_sheet.delay(
        user_id=message.from_user.id,
        step="phone",
        data=phone_number
    )

    try:
        await db.save_application_partially(
            user_id=message.from_user.id,
            part="phone_number",
            data=phone_number
        )
    except Exception as e:
        logging.error(f"Error saving phone number: {e}")

    await message.answer("Yoshingizni kiriting.", reply_markup=back_keyboard())
    await state.update_data(phone_number=phone_number)
    await state.update_data(step="age_input")
    await state.set_state("age_input")

@dp.message_handler(state="age_input")
async def handle_age_input(message: types.Message, state: FSMContext):
    """
    Handle the user's input of their age.
    """

    if message.text == "🔙 Orqaga":

        await message.answer("Telefon raqamingizni yuboring 👇", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True),
                ],
                [
                    types.KeyboardButton(text="🔙 Orqaga"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        ))

        await state.update_data(step="phone_input")

        await state.set_state("phone_input")
        return
    
    # Validate the age input
    if not message.text.isdigit() or not (14 <= int(message.text) <= 100):
        await message.answer("Iltimos, yoshingizni faqat raqamda kiriting (14-100 oralig‘ida).")
        return

    user_data = await state.get_data()
    selected_vacancy = user_data.get("selected_vacancy")
    age = message.text

    # Save the application to the database
    await db.save_application_partially(
        user_id=message.from_user.id,
        part="age",
        data=age
    )
    update_google_sheet.delay(
        user_id=message.from_user.id,
        step="age",
        data=age
    )

    await message.answer("Qilgan ishlaringizdan namunalar yuboring. Fayl yoki link ko'rinishida yuboring.", reply_markup=back_keyboard())
    await state.update_data(age=age)
    await state.update_data(step="portfolio_input")
    await state.set_state("portfolio_input")

@dp.message_handler(state="portfolio_input", content_types=[types.ContentType.TEXT, types.ContentType.DOCUMENT])
async def handle_portfolio_input(message: types.Message, state: FSMContext):
    """
    Handle the user's input of their portfolio.
    """
    if message.text == "🔙 Orqaga":
        await message.answer("Yoshingizni kiriting.", reply_markup=back_keyboard())
        await state.set_state("age_input")
        return

    user_data = await state.get_data()
    selected_vacancy = user_data.get("selected_vacancy")
    portfolio = message.text if message.content_type == 'text' else message.document.file_id
    portfolio_type = "link" if message.content_type == 'text' else "document"
    

    # Save the application to the database
    await db.save_application_partially(
        user_id=message.from_user.id,
        part="portfolio",
        data=portfolio
    )
    await db.save_application_partially(
        user_id=message.from_user.id,
        part="portfolio_type",
        data=portfolio_type
    )
    
    if portfolio_type == "link":
        update_google_sheet.delay(
            user_id=message.from_user.id,
            step="portfolio",
            data=portfolio
        )
    else:
        update_google_sheet.delay(
            user_id=message.from_user.id,
            step="portfolio",
            data="Fayl ko'rinishida yuborildi"
        )
    await message.answer("O'zingiz haqingizda ma'lumot yuboring.", reply_markup=back_keyboard())
    await state.update_data(portfolio=portfolio)
    await state.update_data(portfolio_type=portfolio_type)
    await state.update_data(step="about_input")
    await state.set_state("about_input")

@dp.message_handler(state="portfolio_input", content_types=types.ContentType.ANY)
async def handle_portfolio_input_text(message: types.Message, state: FSMContext):
    """
    Handle the user's input of their portfolio.
    """
    if message.text == "🔙 Orqaga":
        await message.answer("Yoshingizni kiriting.", reply_markup=back_keyboard())
        await state.set_state("age_input")
        return

    await message.answer("Iltimos, fayl yoki link ko'rinishida yuboring.", reply_markup=back_keyboard())
    await state.set_state("portfolio_input")

@dp.message_handler(state="about_input")
async def handle_about_input(message: types.Message, state: FSMContext):
    """
    Handle the user's input of their about information.
    """
    if message.text == "🔙 Orqaga":
        await message.answer("Qilgan ishlaringizdan namunalar yuboring. Fayl yoki link ko'rinishida yuboring .", reply_markup=back_keyboard())
        await state.set_state("portfolio_input")
        return
    
    user_data = await state.get_data()
    selected_vacancy = user_data.get("selected_vacancy")
    about = message.text

    # Save the application to the database
    await db.save_application_partially(
        user_id=message.from_user.id,
        part="about",
        data=about
    )
    update_google_sheet.delay(
        user_id=message.from_user.id,
        step="about",
        data=about
    )

    task = await db.get_technical_task_for_vacancy(selected_vacancy)
    if task:
        user_task, created = await db.get_or_create_user_task(
            user_id=message.from_user.id,
            task_id=task['id']
        )
        if created:
            application_id = await db.save_application_partially(
                user_id=message.from_user.id,
                part="status",
                data='in_task'
            )
            send_application_to_admins.delay(application_id)
            await message.answer(f"Texnik topshiriq:\n\n{user_task['task']}\n\n"
                                f"Topshiriqni qancha muddatda yakunlay olasiz?", reply_markup=get_deadline_keyboard(user_task['id']))
            await db.update_user_task(
                user_task_id=user_task['id'],
                field='started_at',
                value=timezone.now()
            )
            # update_google_sheet.delay(
            #     user_id=message.from_user.id,
            #     step="task",
            #     data=user_task['task']
            # )

            # update_google_sheet.delay(
            #     user_id=message.from_user.id,
            #     step="task_start",
            #     data=timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            # )
            # update_google_sheet.delay(
            #     user_id=message.from_user.id,
            #     step="deadline",
            #     data=user_task['deadline']
            # )
            # update_google_sheet.delay(
            #     user_id=message.from_user.id,
            #     step="status",
            #     data="Vazifa bajarmoqda"
            # )
            update_google_sheet.apply_async(
                kwargs={
                    'user_id': message.from_user.id,
                    'step': 'task',
                    'data': user_task['task'][:50]
                },
                countdown=1  # 1 soniyadan keyin bajariladi
            )

            update_google_sheet.apply_async(
                kwargs={
                    'user_id': message.from_user.id,
                    'step': 'task_start',
                    'data': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                countdown=2  # 2 soniyadan keyin bajariladi
            )

            # update_google_sheet.apply_async(
            #     kwargs={
            #         'user_id': message.from_user.id,
            #         'step': 'deadline',
            #         'data': user_task['deadline']
            #     },
            #     countdown=3  # 3 soniyadan keyin bajariladi
            # )

            update_google_sheet.apply_async(
                kwargs={
                    'user_id': message.from_user.id,
                    'step': 'status',
                    'data': "Vazifa bajarmoqda"
                },
                countdown=4  # 4 soniyadan keyin bajariladi
            )

            await state.update_data(task_id=task['id'])
            await state.finish()
            return
        else:
            await message.answer(f"Sizga ushbu texnik topshiriq allaqachon berilgan. Iltimos, avvalgi topshiriqni bajaring.\n\n"
                                 f"{user_task['task']}\n\n"
                                 f"Vazifa uchun deadline(muddat) tanlang.", reply_markup=get_deadline_keyboard(user_task['id']))
            await state.finish()
            return
        
    else:
        await state.finish()
        await message.answer("Hozirda texnik topshiriq mavjud emas.\nSiz bilan bog'lanamiz.\nRahmat!", reply_markup=types.ReplyKeyboardRemove())
        return
    