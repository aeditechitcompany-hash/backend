from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

class ProcessStage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.name}"


class StudentProcess(models.Model):
    student = models.OneToOneField(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="process",
    )

    current_stage = models.ForeignKey(
        ProcessStage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="students",
    )

    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Process({self.student.user.email})"

    @transaction.atomic
    def complete_current_stage(self, updated_by=None, remarks=""):
        """
        Complete the student's current stage and move them
        to the next process stage.
        """

        if self.current_stage is None:
            raise ValueError(
                "This student does not have a current process stage."
            )

        current_stage = (
            ProcessStage.objects
            .select_for_update()
            .get(pk=self.current_stage_id)
        )

        # ---------------------------------------------------------
        # FIND CURRENT HISTORY
        # ---------------------------------------------------------

        history, _ = ProcessStageHistory.objects.get_or_create(
            student_process=self,
            stage=current_stage,
            defaults={
                "status": ProcessStageHistory.Status.IN_PROGRESS,
            },
        )

        # ---------------------------------------------------------
        # COMPLETE CURRENT STAGE
        # ---------------------------------------------------------

        history.status = ProcessStageHistory.Status.COMPLETED
        history.completed_at = timezone.now()
        history.updated_by = updated_by

        if remarks:
            history.remarks = remarks

        history.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_by",
                "remarks",
            ]
        )

        # ---------------------------------------------------------
        # FIND NEXT STAGE
        # ---------------------------------------------------------

        next_stage = (
            ProcessStage.objects
            .filter(order__gt=current_stage.order)
            .order_by("order")
            .first()
        )

        # ---------------------------------------------------------
        # NO NEXT STAGE
        # ---------------------------------------------------------

        if next_stage is None:
            return {
                "previous_stage": current_stage,
                "current_stage": current_stage,
                "completed": True,
                "finished": True,
            }

        # ---------------------------------------------------------
        # MOVE TO NEXT STAGE
        # ---------------------------------------------------------

        self.current_stage = next_stage

        self.save(
            update_fields=[
                "current_stage",
                "updated_at",
            ]
        )

        # ---------------------------------------------------------
        # CREATE NEXT HISTORY
        # ---------------------------------------------------------

        ProcessStageHistory.objects.update_or_create(
            student_process=self,
            stage=next_stage,
            defaults={
                "status": ProcessStageHistory.Status.IN_PROGRESS,
                "updated_by": updated_by,
            },
        )

        return {
            "previous_stage": current_stage,
            "current_stage": next_stage,
            "completed": True,
            "finished": False,
        }


class ProcessStageHistory(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    student_process = models.ForeignKey(
        StudentProcess,
        on_delete=models.CASCADE,
        related_name="stage_history",
    )

    stage = models.ForeignKey(
        ProcessStage,
        on_delete=models.CASCADE,
        related_name="history_entries",
    )

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["stage__order"]
        verbose_name_plural = "Process stage histories"

    def __str__(self):
        return (
            f"{self.student_process_id} - "
            f"{self.stage.name} ({self.status})"
        )