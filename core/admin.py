from django.contrib import admin

from .models import DisasterReport, Profile, ResponseUpdate


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "phone")


class ResponseUpdateInline(admin.TabularInline):
    model = ResponseUpdate
    extra = 0


@admin.register(DisasterReport)
class DisasterReportAdmin(admin.ModelAdmin):
    list_display = ("code", "disaster_type", "title", "location", "severity", "status", "updated_at")
    list_filter = ("disaster_type", "severity", "status", "is_public")
    search_fields = ("code", "title", "location", "description")
    readonly_fields = ("code", "created_at", "updated_at")
    inlines = [ResponseUpdateInline]


@admin.register(ResponseUpdate)
class ResponseUpdateAdmin(admin.ModelAdmin):
    list_display = ("report", "author", "new_status", "created_at")
