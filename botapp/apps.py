from django.apps import AppConfig
import json

class BotappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'botapp'

    def ready(self):
        import botapp.signals

        # schedule, _ = IntervalSchedule.objects.get_or_create(
        #     every=1,
        #     period=IntervalSchedule.HOURS,
        # )

        # PeriodicTask.objects.get_or_create(
        #     interval=schedule,
        #     name='Check user task deadlines',
        #     task='botapp.tasks.check_task_deadlines',  # full path to the Celery task
        #     defaults={'args': json.dumps([])},
        # )