from django.shortcuts import render

from django.contrib.auth.models import User
from django.utils.timezone import localtime

from tracker.models import WorkSession, Screenshot

from django.db.models import Avg, Sum
from datetime import timedelta
from django.utils import timezone

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Company,
    EmployeeProfile
)


class LoginView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:

            return Response({
                "error": "Email and password required"
            }, status=400)

        user = authenticate(
            username=email,
            password=password
        )

        if user is None:

            return Response({
                "error": "Invalid credentials"
            }, status=401)

        profile = EmployeeProfile.objects.filter(
            user=user
        ).first()

        refresh = RefreshToken.for_user(user)

        return Response({

            "access": str(refresh.access_token),

            "refresh": str(refresh),

            "user": {

                "id": user.id,

                "email": user.email,

                "role":
                profile.role if profile else "",

                "company":
                profile.company.name if profile else ""
            }
        })



@method_decorator(csrf_exempt, name='dispatch')
class RegisterCompanyView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        company_name = request.data.get(
            "company_name"
        )

        email = request.data.get(
            "email"
        )

        password = request.data.get(
            "password"
        )

        if not company_name:

            return Response({
                "error":
                "Company name required"
            }, status=400)

        if not email:

            return Response({
                "error":
                "Email required"
            }, status=400)

        if not password:

            return Response({
                "error":
                "Password required"
            }, status=400)

        if User.objects.filter(
            username=email
        ).exists():

            return Response({
                "error":
                "Email already exists"
            }, status=400)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        company = Company.objects.create(
            name=company_name,
            owner=user
        )

        EmployeeProfile.objects.create(
            user=user,
            company=company,
            role="owner"
        )

        refresh = RefreshToken.for_user(
            user
        )

        return Response({

            "message":
            "Company created",

            "access":
            str(refresh.access_token),

            "refresh":
            str(refresh),

            "user": {

                "id":
                user.id,

                "email":
                user.email,

                "role":
                "owner",

                "company":
                company.name
            }
        })




class CreateEmployeeView(APIView):


    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            profile = EmployeeProfile.objects.filter(
                user=request.user
            ).first()

            print("LOGIN USER:", request.user)
            print("PROFILE:", profile)

            if not profile:

                return Response({
                    "error": "Profile not found"
                }, status=400)

            # SECURITY CHECK 🔥

            if profile.role not in [
                "owner",
                "manager"
            ]:

                return Response({
                    "error":
                    "Permission denied"
                }, status=403)

            print("ROLE:", profile.role)

            name = request.data.get("name", "")

            email = request.data.get("email")

            password = request.data.get(
                "password"
            )

            role = request.data.get(
                "role",
                "employee"
            )

            if not email:

                return Response({
                    "error":
                    "Email required"
                }, status=400)

            if not password:

                return Response({
                    "error":
                    "Password required"
                }, status=400)

            if User.objects.filter(
                username=email
            ).exists():

                return Response({
                    "error":
                    "Email already exists"
                }, status=400)

            user = User.objects.create_user(

                username=email,

                email=email,

                password=password
            )

            parts = name.strip().split(" ", 1)

            user.first_name = parts[0] if len(parts) > 0 else ""

            user.last_name = parts[1] if len(parts) > 1 else ""

            user.save()

            EmployeeProfile.objects.create(

                user=user,

                company=profile.company,

                role=role
            )

            return Response({

                "message":
                "Employee created successfully"
            })

        except Exception as e:

            print(e)

            return Response({
                "error": str(e)
            }, status=500)

        

class CompanyEmployeesView(APIView):
        
    permission_classes = [IsAuthenticated]

    def get(self, request):

        current_profile = EmployeeProfile.objects.get(
            user=request.user
        )

        profiles = EmployeeProfile.objects.filter(
            company=current_profile.company
        ).select_related("user")

        employees = []

        total_employees = profiles.count()

        active_employees = profiles.filter(
            is_online=True
        ).count()

        live_sessions = WorkSession.objects.filter(
            task__company=current_profile.company,
            is_active=True
        ).count()

        screenshots_today = Screenshot.objects.filter(
            company=current_profile.company,
            created_at__date=timezone.now().date()
        ).count()

        total_hours = 0

        total_productivity = 0

        top_employee = None

        # EMPLOYEE DATA

        today = timezone.now().date()

        for profile in profiles:

                # AUTO OFFLINE AFTER 2 MINUTES

            if profile.last_activity:

                diff = (
                    timezone.now()
                    -
                    profile.last_activity
                ).total_seconds()

                if diff > 120:

                    profile.is_online = False
                    profile.save(
                        update_fields=["is_online"]
                    )

            productivity = (
                profile.productivity_percentage or 0
            )

            hours = (
                profile.total_working_hours or 0
            )

            total_hours += hours

            total_productivity += productivity

            today_seconds = WorkSession.objects.filter(
                user=profile.user,
                created_at__date=today
            ).aggregate(
                total=Sum("total_seconds")
            )["total"] or 0

            today_hours = round(
                today_seconds / 3600,
                1
            )

            weekly_seconds = WorkSession.objects.filter(
                user=profile.user,
                created_at__date__gte=today - timedelta(days=6)
            ).aggregate(
                total=Sum("total_seconds")
            )["total"] or 0

            weekly_hours = round(
                weekly_seconds / 3600,
                1
            )

            if (
                not top_employee
                or productivity >
                top_employee.productivity_percentage
            ):
                top_employee = profile

            employees.append({

                "id":
                profile.user.id,

                "email":
                profile.user.email,

                "role":
                profile.role,

                "is_online":
                profile.is_online,

                "is_on_break":
                profile.is_on_break,

                "last_seen":
                localtime(
                    profile.last_activity
                ).strftime(
                    "%d %b %I:%M %p"
                ) if profile.last_activity else None,

                "today_hours":
                today_hours,

                "weekly_hours":
                weekly_hours,

                "productivity":
                round(
                    productivity,
                    1
                ),

                "name": (
                    profile.user.get_full_name()
                    if profile.user.get_full_name()
                    else profile.user.username
                ),

                "join_date": profile.joined_at.strftime(
                    "%d %b %Y"
                ),

                "total_hours": round(
                    profile.total_working_hours,
                    1
                ),

                "avg_productivity": round(
                    profile.productivity_percentage,
                    1
                ),

                "break_minutes": round(
                    profile.total_break_seconds / 60,
                    1
                ),

                "latest_activity": localtime(
                    profile.last_activity
                ).strftime(
                    "%d %b %Y %I:%M %p"
                ) if profile.last_activity else "Never",
            })
        # AVG PRODUCTIVITY

        avg_productivity = 0

        if total_employees > 0:

            avg_productivity = round(
                total_productivity /
                total_employees,
                1
            )


        top_employee_today_hours = 0

        if top_employee:

            top_seconds = WorkSession.objects.filter(
                user=top_employee.user,
                created_at__date=today
            ).aggregate(
                total=Sum("total_seconds")
            )["total"] or 0

            top_employee_today_hours = round(
                top_seconds / 3600,
                1
            )

        # WEEKLY PRODUCTIVITY GRAPH

        weekly_data = []

        for i in range(6, -1, -1):

            date = (
                timezone.now().date()
                - timedelta(days=i)
            )

            daily_profiles = profiles.filter(
                last_activity__date=date
            )

            avg = daily_profiles.aggregate(
                avg=Avg(
                    "productivity_percentage"
                )
            )["avg"] or 0

            weekly_data.append({

                "day":
                date.strftime("%a"),

                "productivity":
                round(avg, 1),
            })

        return Response({

            "employees":
            employees,

            "total_employees":
            total_employees,

            "active_employees":
            active_employees,

            "screenshots_today": screenshots_today,

            "live_sessions": live_sessions,

            "avg_productivity":
            avg_productivity,

            "top_employee": {

                "email":
                top_employee.user.email,

                "productivity":
                round(
                    top_employee.productivity_percentage,
                    1
                ),

                "today_hours":
                top_employee_today_hours,

            } if top_employee else None,

            "weekly_productivity":
            weekly_data,
        })


class DeleteEmployeeView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        employee = User.objects.get(
            id=pk
        )

        employee_profile = EmployeeProfile.objects.get(
            user=employee
        )

        if employee_profile.company != profile.company:

            return Response(
                {"error": "Permission denied"},
                status=403
            )

        if employee_profile.role == "owner":
            return Response(
                {"error":"Owner cannot be deleted"},
                status=400
            )    

        employee.delete()

        return Response({
            "message": "Employee deleted"
        })


class EditEmployeeView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        current_profile = EmployeeProfile.objects.get(
            user=request.user
        )

        employee = User.objects.get(id=pk)

        employee_profile = EmployeeProfile.objects.get(
            user=employee
        )

        if employee_profile.company != current_profile.company:
            return Response(
                {"error": "Permission denied"},
                status=403
            )

        name = request.data.get("name")
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role")

        # NAME UPDATE
        if name is not None:

            parts = name.strip().split(" ", 1)

            employee.first_name = (
                parts[0] if len(parts) > 0 else ""
            )

            employee.last_name = (
                parts[1] if len(parts) > 1 else ""
            )

        # EMAIL UPDATE
        if email:

            if User.objects.filter(
                username=email
            ).exclude(id=employee.id).exists():

                return Response(
                    {"error":"Email already exists"},
                    status=400
                )
            employee.email = email
            employee.username = email

        # PASSWORD UPDATE
        if password:
            employee.set_password(password)

        employee.save()

        # ROLE UPDATE
        if role:
            employee_profile.role = role
            employee_profile.save()

        return Response({
            "message": "Employee updated successfully",

            "employee": {
                "id": employee.id,
                "name": employee.get_full_name(),
                "email": employee.email,
                "role": employee_profile.role,
            }
        })


class HeartbeatView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        profile.is_online = True
        profile.last_activity = timezone.now()

        profile.save()

        return Response({
            "status": "ok"
        })


class StartBreakView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        profile.is_on_break = True
        profile.break_started_at = timezone.now()

        profile.save()

        return Response({
            "message": "Break started"
        })


class EndBreakView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = EmployeeProfile.objects.get(
            user=request.user
        )

        if profile.break_started_at:

            seconds = int(
                (
                    timezone.now()
                    -
                    profile.break_started_at
                ).total_seconds()
            )

            profile.total_break_seconds += seconds

        profile.is_on_break = False
        profile.break_started_at = None

        profile.save()

        return Response({
            "message": "Break ended"
        })                    