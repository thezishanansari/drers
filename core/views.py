"""Views for DRERS."""

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssignForm, LoginForm, RegisterForm, ReportForm, StatusUpdateForm
from .models import DisasterReport, ResponseUpdate, Role, Status


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def role_of(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser or user.is_staff:
        return Role.ADMIN
    return getattr(user.profile, "role", Role.CITIZEN)


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
def public_alerts(request):
    """Public Disaster Alerts page — no login required."""
    alerts = DisasterReport.objects.filter(is_public=True).exclude(status=Status.REJECTED)
    return render(request, "public_alerts.html", {"alerts": alerts})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"].strip(),
            password=form.cleaned_data["password"],
        )
        if user is None:
            messages.error(request, "Invalid username or password. Please try again.")
        elif not user.is_active:
            messages.error(request, "This account has been deactivated.")
        else:
            auth_login(request, user)
            return redirect(request.POST.get("next") or "dashboard")

    return render(request, "login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()                      # always a Citizen
        auth_login(request, user)
        messages.success(request, "Welcome to DRERS. Your citizen account is ready.")
        return redirect("dashboard")

    return render(request, "register.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect("login")


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------
@login_required
def dashboard(request):
    """One entry point that renders the right dashboard for the role."""
    role = role_of(request.user)
    if role == Role.ADMIN:
        return admin_dashboard(request)
    if role == Role.RESPONDER:
        return responder_dashboard(request)
    return citizen_dashboard(request)


def _stats(qs):
    return qs.aggregate(
        total=Count("id"),

        pending=Count(
            "id",
            filter=Q(status=Status.PENDING)
        ),

        assigned=Count(
            "id",
            filter=Q(status=Status.ASSIGNED)
        ),

        in_progress=Count(
            "id",
            filter=Q(status=Status.IN_PROGRESS)
        ),

        resolved=Count(
            "id",
            filter=Q(status=Status.RESOLVED)
        ),

        critical=Count(
            "id",
            filter=Q(severity="critical")
        ),
    )


@login_required
def citizen_dashboard(request):
    reports = DisasterReport.objects.filter(reporter=request.user)
    return render(
        request,
        "dashboard_citizen.html",
        {"reports": reports, "stats": _stats(reports), "role_name": "Citizen"},
    )


@login_required
def responder_dashboard(request):
    reports = DisasterReport.objects.filter(assigned_to=request.user)
    unassigned = DisasterReport.objects.filter(assigned_to__isnull=True, status=Status.PENDING)
    return render(
        request,
        "dashboard_responder.html",
        {
            "reports": reports,
            "unassigned": unassigned,
            "stats": _stats(reports),
            "role_name": "Emergency Responder",
        },
    )


@login_required
def admin_dashboard(request):
    reports = DisasterReport.objects.all()
    return render(
        request,
        "dashboard_admin.html",
        {"reports": reports, "stats": _stats(reports), "role_name": "Administrator"},
    )


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
@login_required
def report_create(request):
    form = ReportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.save()
        ResponseUpdate.objects.create(
            report=report, author=request.user, message="Report submitted.",
            new_status=Status.PENDING,
        )
        messages.success(request, f"Report {report.code} submitted. Thank you.")
        return redirect("report_detail", code=report.code)

    return render(request, "report_form.html", {"form": form})


@login_required
def report_detail(request, code):
    report = get_object_or_404(DisasterReport, code=code)
    role = role_of(request.user)

    # Citizens may only open their own reports
    if role == Role.CITIZEN and report.reporter != request.user:
        messages.error(request, "You do not have permission to view that report.")
        return redirect("dashboard")

    status_form = StatusUpdateForm(initial={"new_status": report.status})
    assign_form = AssignForm(initial={"responder": report.assigned_to})

    return render(
        request,
        "report_detail.html",
        {
            "report": report,
            "updates": report.updates.all(),
            "status_form": status_form,
            "assign_form": assign_form,
            "can_manage": role in (Role.ADMIN, Role.RESPONDER),
            "is_admin": role == Role.ADMIN,
        },
    )


@login_required
def report_update_status(request, code):
    report = get_object_or_404(DisasterReport, code=code)
    if role_of(request.user) not in (Role.ADMIN, Role.RESPONDER):
        messages.error(request, "Only responders and administrators can update a report.")
        return redirect("report_detail", code=code)

    form = StatusUpdateForm(request.POST)
    if form.is_valid():
        report.status = form.cleaned_data["new_status"]
        report.save()
        ResponseUpdate.objects.create(
            report=report,
            author=request.user,
            message=form.cleaned_data["message"] or f"Status changed to {report.get_status_display()}.",
            new_status=report.status,
        )
        messages.success(request, f"{report.code} updated to {report.get_status_display()}.")
    return redirect("report_detail", code=code)


@login_required
def report_assign(request, code):
    report = get_object_or_404(DisasterReport, code=code)
    if role_of(request.user) != Role.ADMIN:
        messages.error(request, "Only administrators can assign responders.")
        return redirect("report_detail", code=code)

    form = AssignForm(request.POST)
    if form.is_valid():
        report.assigned_to = form.cleaned_data["responder"]
        if report.status == Status.PENDING:
            report.status = Status.ASSIGNED
        report.save()
        ResponseUpdate.objects.create(
            report=report,
            author=request.user,
            message=f"Assigned to {report.assigned_to.get_full_name() or report.assigned_to.username}.",
            new_status=report.status,
        )
        messages.success(request, "Responder assigned.")
    return redirect("report_detail", code=code)
