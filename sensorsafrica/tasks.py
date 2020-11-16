from celery import shared_task
from django.core.management import call_command


# @shared_task
# def calculate_data_statistics():
#     call_command("calculate_data_statistics")


@shared_task
def archive_data():
    call_command("upload_to_ckan")


@shared_task
def cache_lastactive_nodes():
    call_command("cache_lastactive_nodes")


# @shared_task
# def cache_static_json_data():
#     call_command("cache_static_json_data", interval='5m')


# @shared_task
# def cache_static_json_data_1h_24h():
#     call_command("cache_static_json_data", interval='1h')
#     call_command("cache_static_json_data", interval='24h')
