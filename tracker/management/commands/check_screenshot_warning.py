from django.core.management.base import BaseCommand

from tracker.models import Screenshot

from django.utils import timezone

from datetime import timedelta


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        six_days_ago = (
            timezone.now() -
            timedelta(days=6)
        )

        screenshots = Screenshot.objects.filter(
                created_at__lt=six_days_ago,
                is_warning_sent=False
            )

        for shot in screenshots:

            print(
                f"Warning for {shot.user.username}"
            )

            shot.is_warning_sent = True
            shot.save()