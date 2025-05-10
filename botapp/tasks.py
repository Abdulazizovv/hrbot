from celery import shared_task
from utils.sheets.main import write_to_google_sheet
from django.utils import timezone
from datetime import timedelta
import threading
from asgiref.sync import async_to_sync
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from botapp.models import Application, BotUser

TOKEN = os.getenv("BOT_TOKEN")

bot = TeleBot(token=TOKEN)


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} kun")
    if hours:
        parts.append(f"{hours} soat")
    if minutes:
        parts.append(f"{minutes} daqiqa")

    return ' '.join(parts) if parts else "Kamida 1 daqiqa"


@shared_task
def update_google_sheet(user_id, step, data):
    """
    Celery task to update Google Sheets with the provided data.
    """
    write_to_google_sheet(user_id, step, data)


@shared_task
def send_application_to_admins(application_id):
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Sending application to admins for application_id: {application_id}")

    application = Application.objects.filter(id=application_id).first()
    if not application:
        logger.warning(f"Application with id {application_id} not found.")
        return
    
    admins = BotUser.objects.filter(is_admin=True).values_list('user_id', flat=True)
    if not admins:
        logger.warning("No admins found.")
        return
    for admin in admins:
        if application.portfolio_type == "document" and application.portfolio:
            bot.send_document(
                chat_id=admin,
                document=application.portfolio,
                caption=(
                    f"Yangi ariza {application.name}:\n\n"
                    f"Ismi: {application.name}\n"
                    f"Telefon raqami: {application.phone_number}\n"
                    f"Yosh: {application.age}\n"
                    f"Yo'nalish: {application.vacancy.name or 'N/A'}\n"
                    f"Telegram: {'@' + application.user.username if application.user.username else 'N/A'}\n"
                    f"Holati: {application.get_status_display()}\n"
                    f"Vaqti: {application.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

                )
            )
        else:
            bot.send_message(
                chat_id=admin,
                text=(
                    f"Yangi ariza {application.name}:\n\n"
                    f"Ismi: {application.name}\n"
                    f"Telefon raqami: {application.phone_number}\n"
                    f"Yoshi: {application.age}\n"
                    f"Yo'nalish: {application.vacancy or 'N/A'}\n"
                    f"Portfolio: {application.portfolio or 'N/A'}\n"
                    f"Holati: {application.get_status_display()}\n"
                    f"Telegram: {'@' + application.user.username if application.user.username else 'N/A'}\n"
                    f"Vaqti: {application.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
            )


@shared_task
def check_task_deadlines():
    from botapp.models import UserTask
    from django.utils import timezone
    from datetime import timedelta
    import logging
    from time import sleep

    logger = logging.getLogger(__name__)
    logger.info("Checking task deadlines...")

    now = timezone.localtime()
    upcoming = now + timedelta(days=3)
    tasks = UserTask.objects.filter(status="pending")
    logger.info(f"Found {tasks.count()} pending tasks.")
    if not tasks:
        logger.info("No pending tasks found.")
        return
    
    for task in tasks:
        timeleft = task.deadline - now
        now = timezone.localtime()
        print(f"Task {task.id} deadline: {task.deadline}, time left: {timeleft}")
        if now > task.deadline:
            logger.info(f"Task {task.id} deadline has passed.")
            task.status = 'rejected'
            task.save()
            try:
                bot.send_message(
                    chat_id=task.user.user_id,
                    text="❌ Kechirasiz, vazifa muddati tugadi va arizangiz rad etildi."
                )
                sleep(0.3)
            except Exception as e:
                logger.error(f"Failed to send message to user {task.user.user_id}: {e}")
            return
        elif timeleft <= timedelta(hours=24):
            logger.info(f"Task {task.id} deadline is approaching.")
            try:
                bot.send_message(
                    chat_id=task.user.user_id,
                    text=f"⏰ Diqqat! Sizning vazifangiz uchun {task.deadline.strftime('%Y-%m-%d')} sanasigacha atigi {format_timedelta(timeleft)} kun qoldi."
                )
                sleep(0.3)
            except Exception as e:
                logger.error(f"Failed to send message to user {task.user.user_id}: {e}")



@shared_task
def send_notification(user_id, text, task_id=None):
    """
    Celery task to send a notification to a user.
    """
    from time import sleep
    try:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                "❌ Bekor qilish",
                callback_data=f"cancel_task_{task_id}"
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                "✅ Tasdiqlash",
                callback_data=f"confirm_task_{task_id}"
            )
        )
        if not task_id:
            keyboard = None
        bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)
        sleep(0.3) 
    except Exception as e:
        print(f"Error sending message to user {user_id}: {e}")