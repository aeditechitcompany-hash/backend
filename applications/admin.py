from django.contrib import admin
from .models import Application, ApplicationStatusHistory


class StatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "university", "course", "status", "applied_date")
    list_filter = ("status", "university")
    search_fields = ("student__user__email", "university__name")
    inlines = [StatusHistoryInline]
