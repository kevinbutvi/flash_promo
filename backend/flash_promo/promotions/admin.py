from django.contrib import admin
from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "cuil", "is_active")
    search_fields = ("first_name", "last_name", "email", "cuil")
    list_filter = ("is_active", "birth_date")
    ordering = ("last_name", "first_name")
