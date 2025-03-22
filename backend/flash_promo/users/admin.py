from django.contrib import admin
from .models import UserSegment, ClientProfile


@admin.register(UserSegment)
class UserSegmentAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "latitude", "longitude", "last_notification_date")
    list_filter = ("last_notification_date",)
    search_fields = ("user__username",)
