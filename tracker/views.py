import profile
from urllib import request, response

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from accounts.models import EmployeeProfile

from django.utils import timezone
from django.utils.timezone import now

from django.db.models import Sum
from django.db.models.functions import TruncDate


from .models import WorkSession, Task, Screenshot

from .serializers import (
    TaskSerializer,
    ScreenshotSerializer
)

import zipfile
import os

from django.http import HttpResponse


class TaskListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        tasks = Task.objects.filter(
            user=request.user,
            company=profile.company
        ).order_by("-id")

        serializer = TaskSerializer(
            tasks,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        title = request.data.get("title")

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        task = Task.objects.create(
            user=request.user,
            company=profile.company,
            title=title
        )

        serializer = TaskSerializer(task)

        return Response(serializer.data)


class TaskDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        task = Task.objects.get(
            id=pk,
            user=request.user
        )

        task.delete()

        return Response({
            "message": "Task Deleted"
        })
    

class StartSessionView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        task_id = request.data.get("task_id")

        task = Task.objects.get(
            id=task_id,
            user=request.user
        )

        WorkSession.objects.filter(
            user=request.user,
            is_active=True
        ).update(
            is_active=False
        )

        session = WorkSession.objects.create(
            user=request.user,
            task=task,
            start_time=timezone.now(),
            is_active=True
        )

        return Response({
            "message": "Session Started",
            "session_id": session.id
        })
    
class StopSessionView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            session = WorkSession.objects.get(
                user=request.user,
                is_active=True
            )

            session.end_time = timezone.now()

            total = (
                session.end_time -
                session.start_time
            ).total_seconds()

            session.total_seconds = total

            session.is_active = False

            session.save()

            # UPDATE WORKING HOURS

            profile = EmployeeProfile.objects.get(
                user=request.user
            )

            # BREAK TIME REMOVE

            break_hours = (
                profile.total_break_seconds / 3600
            )

            total_hours = (
                total / 3600
            ) - break_hours

            if total_hours < 0:
                total_hours = 0

            profile.total_working_hours += round(
                total_hours,
                2
            )

            profile.last_activity = timezone.now()

            profile.is_online = False

            profile.is_on_break = False
            profile.break_started_at = None

            profile.save()

            return Response({

                "message":
                "Session Stopped",

                "seconds":
                total,

                "hours":
                round(total_hours, 2)
            })

        except Exception as e:

            print(e)

            return Response({

                "error":
                "No active session"

            }, status=400)
  


class ActiveSessionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        session = WorkSession.objects.filter(
            user=request.user,
            is_active=True
        ).first()

        if not session:

            return Response({
                "is_active": False
            })

        elapsed_seconds = int(
            (
                now() - session.start_time
            ).total_seconds()
        )

        return Response({
            "is_active": True,
            "task_id": session.task.id,
            "task_title": session.task.title,
            "start_time": session.start_time,
            "elapsed_seconds": elapsed_seconds
        })



class ReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        sessions = WorkSession.objects.filter(
            user=request.user
        )

        total_seconds = sessions.aggregate(
                total=Sum("total_seconds")
            )["total"] or 0

        task_report = []

        tasks = Task.objects.filter(
            user=request.user
        )

        for task in tasks:

            task_seconds = WorkSession.objects.filter(
                    user=request.user,
                    task=task
                ).aggregate(
                    total=Sum("total_seconds")
                )["total"] or 0

            task_report.append({
                "task": task.title,
                "seconds": task_seconds
            })

        weekly = WorkSession.objects.filter(
                user=request.user
            ).annotate(
                day=TruncDate("created_at")
            ).values(
                "day"
            ).annotate(
                total=Sum("total_seconds")
            ).order_by("day")

        return Response({

            "total_seconds": total_seconds,

            "task_report": task_report,

            "weekly_report": weekly
        })

class UploadScreenshotView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    parser_classes = (
        MultiPartParser,
        FormParser
    )

    def post(self, request):

        try:

            task_id = request.data.get(
                "task_id"
            )

            image = request.data.get(
                "image"
            )

            if (
                not task_id or
                task_id == ""
            ):

                return Response({
                    "error":
                    "Task ID missing"
                }, status=400)

            if not image:

                return Response({
                    "error":
                    "Image missing"
                }, status=400)

            task = Task.objects.get(
                id=int(task_id),
                user=request.user
            )

            profile = EmployeeProfile.objects.get(
                user=request.user
            )

    active = profile.active_seconds >= profile.idle_seconds

             screenshot = Screenshot.objects.create(
               user=request.user,
               company=profile.company,
               task=task,
               image=image,
            is_active=active
          )
            serializer = ScreenshotSerializer(
                screenshot
            )

            return Response(
                serializer.data
            )

        except Exception as e:

            print(e)

            return Response({
                "error": str(e)
            }, status=500)

class DownloadScreenshotsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        screenshots = Screenshot.objects.filter(
                user=request.user
            )

        response = HttpResponse(
            content_type='application/zip'
        )

        response[
            'Content-Disposition'
        ] = 'attachment; filename=screenshots.zip'

        zip_file = zipfile.ZipFile(
                response,
                'w'
            )

        for shot in screenshots:

            if shot.image:

                zip_file.write(
                    shot.image.path,
                    os.path.basename(
                        shot.image.path
                    )
                )

        zip_file.close()

        return response    
    


class CompanyScreenshotsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        screenshots = Screenshot.objects.filter(
            company=profile.company
        ).order_by("-created_at")

        data = []

        for shot in screenshots:

            data.append({

                "employee":
                shot.user.username,

                "task":
                shot.task.title,

                "image":
                shot.image.url,

                "created_at":
                shot.created_at

                 "is_active":
                shot.is_active
            })

        return Response(data)



class OnlineEmployeesView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        sessions = WorkSession.objects.filter(
            task__company=
            profile.company,
            is_active=True
        )

        data = []

        for session in sessions:

            data.append({

                "employee":
                session.user.username,

                "task":
                session.task.title,

                "started":
                session.start_time
            })

        return Response(data)
    


class UpdateOnlineStatusView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        is_online = request.data.get(
            "is_online",
            False
        )

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        profile.is_online = is_online

        profile.last_activity = timezone.now()

        profile.save()

        return Response({
            "message": "status updated"
        })    
    


class UpdateActivityView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        keyboard = request.data.get(
            "keyboard",
            0
        )

        mouse = request.data.get(
            "mouse",
            0
        )

        idle = request.data.get(
            "idle",
            0
        )

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        active = keyboard + mouse

        profile.active_seconds += active

        profile.idle_seconds += idle

        total = (
            profile.active_seconds +
            profile.idle_seconds
        )

        if total > 0:

            profile.productivity_percentage = round(
                (
                    profile.active_seconds /
                    total
                ) * 100,
                2
            )

        profile.save()

        return Response({
            "message": "activity updated",
            "productivity":
            profile.productivity_percentage
        })