from django.db import models


class Interview(models.Model):
    class Mode(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"
        PHONE = "phone", "Phone"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        RESCHEDULED = "rescheduled", "Rescheduled"

    class Result(models.TextChoices):
        PENDING = "pending", "Pending"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"

    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE, related_name="interviews")
    scheduled_at = models.DateTimeField()
    mode = models.CharField(max_length=16, choices=Mode.choices, default=Mode.ONLINE)
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    interviewer_name = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SCHEDULED)
    result = models.CharField(max_length=16, choices=Result.choices, default=Result.PENDING)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"Interview({self.application_id}, {self.scheduled_at})"
