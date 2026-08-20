from django.conf import settings
from django.db import models


class ProcessStage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.name}"


class StudentProcess(models.Model):
    student = models.OneToOneField("students.StudentProfile", on_delete=models.CASCADE, related_name="process")
    current_stage = models.ForeignKey(ProcessStage, on_delete=models.SET_NULL, null=True, related_name="students")
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Process({self.student.user.email})"


class ProcessStageHistory(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    student_process = models.ForeignKey(StudentProcess, on_delete=models.CASCADE, related_name="stage_history")
    stage = models.ForeignKey(ProcessStage, on_delete=models.CASCADE, related_name="history_entries")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    completed_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["stage__order"]
        verbose_name_plural = "Process stage histories"

    def __str__(self):
        return f"{self.student_process_id} - {self.stage.name} ({self.status})"
