from rest_framework import serializers
from .models import (
    Task,
    Screenshot
)

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"

class ScreenshotSerializer(serializers.ModelSerializer):

    employee = serializers.CharField(
        source="user.email",
        read_only=True
    )

    task_name = serializers.CharField(
        source="task.name",
        read_only=True
    )

    class Meta:
        model = Screenshot
        fields = "__all__"   