from django.urls import path

from .views import (
    TaskListCreateView,
    TaskDeleteView,
    StartSessionView,
    StopSessionView,
    ActiveSessionView,
    ReportView,
    UpdateActivityView,
    UpdateOnlineStatusView,
    UploadScreenshotView,
    DownloadScreenshotsView,
    CompanyScreenshotsView,
    OnlineEmployeesView,    
)

urlpatterns = [

    path(
        "tasks/",
        TaskListCreateView.as_view()
    ),

    path(
        "tasks/delete/<int:pk>/",
        TaskDeleteView.as_view()
    ),

    path(
        "session/start/",
        StartSessionView.as_view()
    ),

    path(
        "session/stop/",
        StopSessionView.as_view()
    ),

    path(
        "active-session/",
        ActiveSessionView.as_view()
    ),

    path(
        "reports/",
        ReportView.as_view()
    ),

    path(
        "upload-screenshot/",
        UploadScreenshotView.as_view()
    ),

    path(
        "download-screenshots/",
        DownloadScreenshotsView.as_view()
    ),

    path(
        "company-screenshots/",
        CompanyScreenshotsView.as_view()
    ),

    path(
        "online-employees/",
        OnlineEmployeesView.as_view()
    ),

    path(
    "update-online-status/",
    UpdateOnlineStatusView.as_view(),
    ),

    path(
    "update-activity/",
    UpdateActivityView.as_view(),
    ),
]