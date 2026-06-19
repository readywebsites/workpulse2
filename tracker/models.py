from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from accounts.models import Company


class Task(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    

class WorkSession(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField(
        null=True,
        blank=True
    )

    total_seconds = models.IntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"
    

class Screenshot(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    image = models.ImageField(
        upload_to="screenshots/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    is_warning_sent = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.user.username} Screenshot"