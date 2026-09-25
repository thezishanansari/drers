"""
Populates the database with the demo users and the three alerts
shown in the DRERS design.

Run with:  python manage.py seed_data
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import DisasterReport, Profile, Role, Severity, Status


class Command(BaseCommand):
    help = "Create demo users and sample disaster reports."

    def handle(self, *args, **options):
        # ------------------------------------------------ users
        users = [
            ("admin", "admin123", "System Administrator", "9800000001", Role.ADMIN, True),
            ("responder1", "resp123", "Ramesh Thapa", "9800000002", Role.RESPONDER, False),
            ("sita", "sita123", "Sita Sharma", "9800000003", Role.CITIZEN, False),
        ]

        created_users = {}
        for username, password, full_name, phone, role, is_super in users:
            first, _, last = full_name.partition(" ")
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last},
            )
            user.first_name, user.last_name = first, last
            user.set_password(password)
            user.is_superuser = is_super
            user.is_staff = is_super
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.phone = phone
            profile.save()

            created_users[username] = user
            self.stdout.write(self.style.SUCCESS(f"  user  {username} / {password}  ({role})"))

        citizen = created_users["sita"]
        responder = created_users["responder1"]

        # ------------------------------------------------ reports
        now = timezone.now()
        reports = [
            {
                "disaster_type": "fire",
                "title": "Fire reported in market shop cluster",
                "description": "Fire broke out in a row of shops. Thick smoke visible, "
                               "fire spreading to adjacent stalls.",
                "location": "Asan Bazaar, Kathmandu",
                "severity": Severity.CRITICAL,
                "status": Status.IN_PROGRESS,
                "assigned_to": responder,
            },
            {
                "disaster_type": "flood",
                "title": "Rising water near Bishnumati river bank",
                "description": "Water level rising fast after continuous rainfall. Several homes "
                               "near the riverbank are at risk of flooding by tonight.",
                "location": "Bishnumati Corridor, Kathmandu",
                "severity": Severity.HIGH,
                "status": Status.ASSIGNED,
                "assigned_to": responder,
            },
            {
                "disaster_type": "landslide",
                "title": "Landslide blocking Mugling–Narayanghat highway",
                "description": "A section of road blocked by debris after overnight rain. "
                               "Vehicles stranded on both sides.",
                "location": "Mugling Highway, Chitwan",
                "severity": Severity.HIGH,
                "status": Status.RESOLVED,
                "assigned_to": responder,
            },
        ]

        for data in reports:
            report, created = DisasterReport.objects.get_or_create(
                title=data["title"],
                defaults={**data, "reporter": citizen, "is_public": True},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  report {report.code} — {report.title}"))

        self.stdout.write(self.style.SUCCESS("\nSeed data ready. Start the server with: python manage.py runserver"))
