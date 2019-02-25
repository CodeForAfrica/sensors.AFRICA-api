from celery import shared_task
from django.core.management import call_command


@shared_task
def calculate_data_statistics():
    call_command("calculate_data_statistics")


@shared_task
def archive_data():
    call_command("upload_to_ckan")
