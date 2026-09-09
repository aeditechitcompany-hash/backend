from django.db import models


class StudentApplication(models.Model):
    student = models.OneToOneField(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="application",
    )

    # ============================================================
    # STEP 4 — INTERVIEW
    # ============================================================

    interview_date = models.DateField(
        blank=True,
        null=True,
    )

    interview_mode = models.CharField(
        max_length=50,
        blank=True,
    )

    interview_result = models.CharField(
        max_length=100,
        blank=True,
    )

    interview_notes = models.TextField(
        blank=True,
    )

    # ============================================================
    # STEP 5 — APPLICATION SUBMISSION
    # ============================================================

    application_ref_no = models.CharField(
        max_length=100,
        blank=True,
    )

    submission_date = models.DateField(
        blank=True,
        null=True,
    )

    confirmation_file_name = models.CharField(
        max_length=255,
        blank=True,
    )

    # ============================================================
    # STEP 6 — OFFER
    # ============================================================

    offer_file_name = models.CharField(
        max_length=255,
        blank=True,
    )

    offer_type = models.CharField(
        max_length=100,
        blank=True,
    )

    offer_expiry_date = models.DateField(
        blank=True,
        null=True,
    )

    # ============================================================
    # STEP 7 — LOC
    # ============================================================

    loc_file_name = models.CharField(
        max_length=255,
        blank=True,
    )

    loc_verified = models.BooleanField(
        default=False,
    )

    # ============================================================
    # STEP 8 — FINAL SELECTION
    # ============================================================

    course_commencement_date = models.DateField(
        blank=True,
        null=True,
    )

    scholarship_status = models.CharField(
        max_length=100,
        blank=True,
    )

    final_selection_notes = models.TextField(
        blank=True,
    )

    final_selection_confirmed = models.BooleanField(
        default=False,
    )

    # ============================================================
    # STEP 9 — VISA
    # ============================================================

    visa_ref_no = models.CharField(
        max_length=100,
        blank=True,
    )

    visa_status_update = models.CharField(
        max_length=100,
        blank=True,
    )

    visa_approval_letter_file_name = models.CharField(
        max_length=255,
        blank=True,
    )

    # ============================================================
    # STEP 10 — FLIGHT
    # ============================================================

    flight_number = models.CharField(
        max_length=100,
        blank=True,
    )

    airline = models.CharField(
        max_length=100,
        blank=True,
    )

    departure_airport = models.CharField(
        max_length=150,
        blank=True,
    )

    arrival_airport = models.CharField(
        max_length=150,
        blank=True,
    )

    departure_date_time = models.DateTimeField(
        blank=True,
        null=True,
    )

    ticket_file_name = models.CharField(
        max_length=255,
        blank=True,
    )

    # ============================================================
    # TIMESTAMPS
    # ============================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Application({self.student.user.email})"