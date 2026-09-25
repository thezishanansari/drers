"""URL patterns for the core app."""

from django.urls import path

from . import views

urlpatterns = [
    # public
    path("", views.login_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("alerts/", views.public_alerts, name="public_alerts"),

    # dashboards
    path("dashboard/", views.dashboard, name="dashboard"),

    # reports
    path("report/new/", views.report_create, name="report_create"),
    path("report/<str:code>/", views.report_detail, name="report_detail"),
    path("report/<str:code>/status/", views.report_update_status, name="report_update_status"),
    path("report/<str:code>/assign/", views.report_assign, name="report_assign"),
]
