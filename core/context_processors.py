"""Makes the live header ticker available on every page."""

from .models import DisasterReport, Status


def ticker(request):
    alerts = (
        DisasterReport.objects.filter(is_public=True)
        .exclude(status=Status.REJECTED)
        .order_by("-updated_at")[:8]
    )
    return {"ticker_alerts": alerts}
