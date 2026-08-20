from django.contrib import admin
from .models import ProcessStage, StudentProcess, ProcessStageHistory


class StageHistoryInline(admin.TabularInline):
    model = ProcessStageHistory
    extra = 0


admin.site.register(ProcessStage)


@admin.register(StudentProcess)
class StudentProcessAdmin(admin.ModelAdmin):
    list_display = ("student", "current_stage", "started_at", "updated_at")
    inlines = [StageHistoryInline]
