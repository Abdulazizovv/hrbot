from celery import shared_task
from utils.sheets.main import write_to_google_sheet


@shared_task
def update_google_sheet(user_id, step, data):
    """
    Celery task to update Google Sheets with the provided data.
    """
    write_to_google_sheet(user_id, step, data)