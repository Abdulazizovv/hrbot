from django.db.models.signals import post_save
from django.dispatch import receiver
from botapp.models import BotUser, Application, UserTask
from botapp.tasks import send_application_to_admins
from botapp.tasks import send_notification



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


@receiver(post_save, sender=Application)
def notify_admins(sender, instance, created, **kwargs):
    """
    Signal to notify admins when a application is sent.
    """
    # if instance.status == "in_task":
    #     send_application_to_admins.delay(instance.id)
    pass
    

@receiver(post_save, sender=UserTask)
def notification_user_task(sender, instance, created, **kwargs):
    """
    Signal to notify admins when a user task is created.
    """
    admins = BotUser.objects.filter(is_admin=True).values_list('user_id', flat=True)
    print(f"Admins: {admins}")
    print(f"Instance: {instance.finished_at}")
    if not created:
        if instance.submission and instance.started_at and instance.finished_at and instance.status == "sent":
            time_spent = format_timedelta(instance.finished_at - instance.started_at)
            for admin in admins:
                
                send_notification.delay(
                    user_id=admin,
                    text=(
                        f"Topshiriq bajarildi:\n\n"
                        f"Ismi: {instance.user.full_name}\n"
                        f"Telegram: {'@' + instance.user.username if instance.user.username else 'N/A'}\n"
                        f"Berilgan vaqti: {instance.started_at.strftime('%Y-%m-%d %H:%M') if instance.started_at else 'Belgilanmagan'}\n"
                        f"Topshirilgan vaqti: {instance.finished_at.strftime('%Y-%m-%d %H:%M') if instance.finished_at else 'Belgilanmagan'}\n"
                        f"Qancha vaqt sarflandi: {time_spent}\n"
                        f"Qancha vaqt so'ragandi: {instance.user_deadline}\n"
                        f"Havola: {instance.submission}\n"
                    ),
                    task_id=instance.id,
                )
            

