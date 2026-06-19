from django.db import models

# Create your models here.

from django.contrib.auth.models import User


class Company(models.Model):

    name = models.CharField(
        max_length=255
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.name

class EmployeeProfile(models.Model):

    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("manager", "Manager"),
        ("employee", "Employee"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="employee"
    )

    is_active_tracking = models.BooleanField(
        default=True
    )

    # ONLINE STATUS

    is_online = models.BooleanField(
        default=False
    )

    last_activity = models.DateTimeField(
        null=True,
        blank=True
    )

    # WORKING TIME

    total_working_hours = models.FloatField(
        default=0
    )

    active_seconds = models.IntegerField(
        default=0
    )

    idle_seconds = models.IntegerField(
        default=0
    )

    productivity_percentage = models.FloatField(
        default=0
    )

    # BREAK TRACKING

    is_on_break = models.BooleanField(
        default=False
    )

    break_started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    total_break_seconds = models.IntegerField(
        default=0
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username