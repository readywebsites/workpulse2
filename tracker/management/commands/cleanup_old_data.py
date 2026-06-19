from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from tracker.models import Screenshot


class Command(BaseCommand):

    help = "Delete screenshots older than 15 days"

    def handle(self, *args, **kwargs):

        cutoff = timezone.now() - timedelta(days=15)

        screenshots = Screenshot.objects.filter(
            created_at__lt=cutoff
        )

        total = screenshots.count()

        for shot in screenshots:

            try:
                if shot.image:
                    shot.image.delete(save=False)
            except Exception:
                pass

        screenshots.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"{total} screenshots deleted"
            )
        )