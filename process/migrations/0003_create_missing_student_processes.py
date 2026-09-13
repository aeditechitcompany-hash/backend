from django.db import migrations


def create_missing_student_processes(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    StudentProfile = apps.get_model("students", "StudentProfile")
    ProcessStage = apps.get_model("process", "ProcessStage")
    StudentProcess = apps.get_model("process", "StudentProcess")
    ProcessStageHistory = apps.get_model(
        "process",
        "ProcessStageHistory",
    )

    # ---------------------------------------------------------
    # Get the first process stage
    # ---------------------------------------------------------
    first_stage = (
        ProcessStage.objects
        .order_by("order", "id")
        .first()
    )

    if first_stage is None:
        return

    # ---------------------------------------------------------
    # Only process actual STUDENT accounts
    # ---------------------------------------------------------
    students = User.objects.filter(role="student")

    for user in students:

        # -----------------------------------------------------
        # Get or create StudentProfile
        # -----------------------------------------------------
        profile, _ = StudentProfile.objects.get_or_create(
            user_id=user.pk,
            defaults={
                "mcq_access": False,
                "book_access": False,
                "current_step": 1,
            },
        )

        # -----------------------------------------------------
        # Get or create StudentProcess
        # -----------------------------------------------------
        student_process, _ = (
            StudentProcess.objects.get_or_create(
                student_id=profile.pk,
                defaults={
                    "current_stage_id": first_stage.pk,
                },
            )
        )

        # -----------------------------------------------------
        # Make sure current stage exists
        # -----------------------------------------------------
        if student_process.current_stage_id is None:
            student_process.current_stage_id = first_stage.pk
            student_process.save(
                update_fields=["current_stage"]
            )

        # -----------------------------------------------------
        # Create initial history
        # -----------------------------------------------------
        ProcessStageHistory.objects.get_or_create(
            student_process_id=student_process.pk,
            stage_id=student_process.current_stage_id,
            defaults={
                "status": "in_progress",
            },
        )


def reverse_create_missing_student_processes(
    apps,
    schema_editor,
):
    # Intentionally do nothing.
    #
    # We don't want reversing this migration to delete
    # StudentProcess records that may have been created
    # legitimately after registration.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("process", "0002_create_student_processes"),
        ("students", "0010_studentapplication_transcript_file"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_missing_student_processes,
            reverse_create_missing_student_processes,
        ),
    ]