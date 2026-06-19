from django.urls import path

from .views import *


urlpatterns = [

    path(
        'login/',
        LoginView.as_view()
    ),

    path(
        "register-company/",
        RegisterCompanyView.as_view()
    ),

    path(
        "create-employee/",
        CreateEmployeeView.as_view()
    ),

    path(
        "company-employees/",
        CompanyEmployeesView.as_view(),
    ),

    path(
    "employees/<int:pk>/",
    DeleteEmployeeView.as_view(),
    ),

    path(
    "employees/<int:pk>/edit/",
    EditEmployeeView.as_view(),
    ),

    path(
    "heartbeat/",
    HeartbeatView.as_view()
    ),

    path(
        "start-break/",
        StartBreakView.as_view()
    ),

    path(
        "end-break/",
        EndBreakView.as_view()
    ),

]