from celery import shared_task
from django.core.management import call_command


@shared_task
def screenshot_warning_task():
    call_command("check_screenshot_warning")


@shared_task
def delete_old_screenshots_task():
    call_command("delete_old_screenshots")


@shared_task
def cleanup_old_data_task():
    call_command("cleanup_old_data")