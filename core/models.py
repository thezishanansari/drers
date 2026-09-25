"""Database models for DRERS."""

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------
class Role(models.TextChoices):
    CITIZEN = "citizen", "Citizen"
    RESPONDER = "responder", "Emergency Responder"
    ADMIN = "admin", "Administrator"


class DisasterType(models.TextChoices):
    FLOOD = "flood", "Flood"
    FIRE = "fire", "Fire"
    LANDSLIDE = "landslide", "Landslide"
    EARTHQUAKE = "earthquake", "Earthquake"
    STORM = "storm", "Storm"
    BUILDING_COLLAPSE = "building_collapse", "Building Collapse"
    ROAD_ACCIDENT = "road_accident", "Road Accident"
    OTHER = "other", "Other Emergency"


class Severity(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    ASSIGNED = "assigned", "Responder Assigned"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    REJECTED = "rejected", "Rejected"


# Emoji shown next to each disaster type in the UI
TYPE_EMOJI = {
    DisasterType.FLOOD: "🌊",
    DisasterType.FIRE: "🔥",
    DisasterType.LANDSLIDE: "🏔️",
    DisasterType.EARTHQUAKE: "🌎",
    DisasterType.STORM: "🌪️",
    DisasterType.BUILDING_COLLAPSE: "🏚️",
    DisasterType.ROAD_ACCIDENT: "🚨",
    DisasterType.OTHER: "⚡",
}


# ---------------------------------------------------------------------------
# Profile — extends the built-in Django User with a role + phone
# ---------------------------------------------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CITIZEN)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "drers_profile"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.user.is_superuser

    @property
    def is_responder(self):
        return self.role == Role.RESPONDER

    @property
    def is_citizen(self):
        return self.role == Role.CITIZEN


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Every User automatically gets a Profile (Citizen by default)."""
    if created:
        role = Role.ADMIN if (instance.is_superuser or instance.is_staff) else Role.CITIZEN
        Profile.objects.create(user=instance, role=role)
    else:
        Profile.objects.get_or_create(user=instance)


# ---------------------------------------------------------------------------
# Disaster report
# ---------------------------------------------------------------------------
class DisasterReport(models.Model):
    code = models.CharField(max_length=20, unique=True, editable=False, db_index=True)

    disaster_type = models.CharField(max_length=30, choices=DisasterType.choices)
    title = models.CharField(max_length=160)
    description = models.TextField()
    location = models.CharField(max_length=160)

    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    reporter = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports"
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assignments"
    )

    photo = models.ImageField(upload_to="reports/", blank=True, null=True)
    is_public = models.BooleanField(default=True, help_text="Show on the public alerts page")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drers_report"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.code} — {self.title}"

    def save(self, *args, **kwargs):
        # Auto-generate the DR-000001 style reference code
        if not self.code:
            last = DisasterReport.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.code = f"DR-{next_id:06d}"
        super().save(*args, **kwargs)

    # --- helpers used by the templates ---
    @property
    def emoji(self):
        return TYPE_EMOJI.get(self.disaster_type, "🚨")

    @property
    def severity_class(self):
        return f"b-{self.severity}"

    @property
    def status_class(self):
        return {
            Status.PENDING: "b-pending",
            Status.ASSIGNED: "b-assigned",
            Status.IN_PROGRESS: "b-progress",
            Status.RESOLVED: "b-resolved",
            Status.REJECTED: "b-pending",
        }.get(self.status, "b-pending")


# ---------------------------------------------------------------------------
# Response log — audit trail of every status change
# ---------------------------------------------------------------------------
class ResponseUpdate(models.Model):
    report = models.ForeignKey(DisasterReport, on_delete=models.CASCADE, related_name="updates")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    new_status = models.CharField(max_length=20, choices=Status.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "drers_response_update"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report.code} · {self.created_at:%b %d %H:%M}"
