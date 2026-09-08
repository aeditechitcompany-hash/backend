from django.db import migrations


def create_student_processes(apps, schema_editor):
    StudentProfile = apps.get_model(
        "students",
        "StudentProfile",
    )
    ProcessStage = apps.get_model(
        "process",
        "ProcessStage",
    )
    StudentProcess = apps.get_model(
        "process",
        "StudentProcess",
    )
    ProcessStageHistory = apps.get_model(
        "process",
        "ProcessStageHistory",
    )

    # Get the first process stage.
    first_stage = (
        ProcessStage.objects
        .order_by("order", "id")
        .first()
    )

    # If no process stages exist, don't create anything.
    if first_stage is None:
        return

    # Create a process for every existing student
    # who doesn't already have one.
    for student in StudentProfile.objects.all():

        student_process, created = (
            StudentProcess.objects.get_or_create(
                student_id=student.pk,
                defaults={
                    "current_stage_id": first_stage.pk,
                },
            )
        )

        # Only create the initial history when
        # the StudentProcess was newly created.
        if created:
            ProcessStageHistory.objects.get_or_create(
                student_process_id=student_process.pk,
                stage_id=first_stage.pk,
                defaults={
                    "status": "in_progress",
                },
            )


def reverse_create_student_processes(apps, schema_editor):
    StudentProcess = apps.get_model(
        "process",
        "StudentProcess",
    )

    # Remove the automatically-created processes
    # when reversing this migration.
    StudentProcess.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("process", "0001_initial"),
        ("students", "0005_studentprofile_current_step_and_more"),
    ]

    operations = [
        migrations.RunPython(
            create_student_processes,
            reverse_create_student_processes,
        ),
    ]