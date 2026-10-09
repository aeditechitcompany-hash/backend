import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage

from .storage import (
    CloudinaryAudioStorage,
    CloudinaryMediaStorage,
)

STAGING_FILE_STORAGE = FileSystemStorage(
    location=settings.MEDIA_ROOT,
)
class QuestionSet(models.Model):

    class Category(models.TextChoices):
        LANGUAGE_PRACTICE = "Language_practice", "Language Practice"
        APTITUDE = "aptitude", "Aptitude"
        VISA_INTERVIEW_PREP = "visa_interview_prep", "Visa Interview Prep"
        GENERAL_KNOWLEDGE = "general_knowledge", "General Knowledge"
        OTHERS = "others", "Others"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    category = models.CharField(
        max_length=32,
        choices=Category.choices,
        default=Category.OTHERS,
    )

    time_limit_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="optional overall time limit",
    )

    passing_score_percentage = models.PositiveSmallIntegerField(
        default=50,
    )

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mcq_sets_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()

class MCQSection(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):

    class QuestionType(models.TextChoices):
        TEXT = "text", "Text Only"
        IMAGE = "image", "Image Based"
        AUDIO = "audio", "Audio Based"
        IMAGE_AUDIO = "image_audio", "Image+Audio"

    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_type = models.CharField(
        max_length=16,
        choices=QuestionType.choices,
        default=QuestionType.TEXT,
    )
    section = models.ForeignKey(
        MCQSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions"
    )

    text = models.TextField(
        blank=True,
        help_text="Question text / prompt.",
    )

    image = models.ImageField(
        upload_to="mcq/questions/images/",
        blank=True,
        null=True,
        storage=CloudinaryMediaStorage(),
    )

    audio = models.FileField(
        upload_to="mcq/questions/audio/",
        blank=True,
        null=True,
        storage=CloudinaryAudioStorage(),
 )

    explanation = models.TextField(
        blank=True,
        help_text="Shown after answering.",
    )

    points = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["question_set", "order", "id"]

    def clean(self):
        if not self.text and not self.image and not self.audio:
            raise ValidationError(
                "A question needs at least one of: text, image, or audio."
            )

    def __str__(self):
        return (
            self.text[:60]
            if self.text
            else f"Question #{self.pk} ({self.question_type})"
        )


class Option(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
    )

    text = models.CharField(
        max_length=500,
        blank=True,
    )

    image = models.ImageField(
        upload_to="mcq/options/images/",
        blank=True,
        null=True,
        storage=CloudinaryMediaStorage(),
    )

    audio = models.FileField(
        upload_to="mcq/options/audio/",
        blank=True,
        null=True,
        storage=CloudinaryAudioStorage(),
    )

    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def clean(self):
        if not self.text and not self.image and not self.audio:
            raise ValidationError(
                "An option needs text, an image, or audio."
            )

    def __str__(self):
        return (
            self.text[:60]
            if self.text
            else f"Option #{self.pk}"
        )


class Attempt(models.Model):

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted", "Submitted"
        EXPIRED = "expired", "Expired"

    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="mcq_attempts",
    )

    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="attempts",
    )

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)

    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
    )

    max_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    passed = models.BooleanField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.user.email} - {self.question_set.title}"

    def grade(self):

        answers = self.answers.select_related(
            "question",
            "selected_option",
        )

        total_points = sum(
            a.question.points for a in answers
        ) or 0

        earned = sum(
            a.question.points
            for a in answers
            if a.is_correct
        )

        self.max_score = total_points
        self.score = earned

        self.percentage = (
            round((earned / total_points) * 100, 2)
            if total_points
            else 0
        )

        self.passed = (
            self.percentage
            >= self.question_set.passing_score_percentage
        )

        self.save(
            update_fields=[
                "max_score",
                "score",
                "percentage",
                "passed",
            ]
        )

        return self


class AttemptAnswer(models.Model):
    """A single answer within an attempt."""

    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    selected_option = models.ForeignKey(
        Option,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="selected_in",
    )

    is_correct = models.BooleanField(default=False)

    answered_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ("attempt", "question")
        ordering = ["question__order"]

    def save(self, *args, **kwargs):
        self.is_correct = bool(
            self.selected_option
            and self.selected_option.is_correct
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attempt_id} - Q{self.question_id}"

class MCQImport(models.Model):
    STATUS_CHOICES = [
        ("uploaded", "Uploaded"),
        ("processing", "Processing"),
        ("review", "Review"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    name = models.CharField(max_length=255)

    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="imports"
    )

    pdf = models.FileField(
        upload_to="mcq/imports/"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="uploaded"
    )

    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    audio_zip = models.FileField(
        upload_to="mcq/imports/audio/",
        blank=True,
        null=True,
    )

    listening_start = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    listening_end = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

class ImportedQuestion(models.Model):
    SECTION_TYPES = [
        ("reading", "Reading"),
        ("listening", "Listening"),
    ]

    import_job = models.ForeignKey(
        MCQImport,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_number = models.PositiveIntegerField()

    section = models.CharField(
        max_length=20,
        choices=SECTION_TYPES,
        default="reading",
    )

    question_text = models.TextField(
        blank=True,
    )

    # --------------------------------------------------------
    # Imported question media
    # --------------------------------------------------------

    question_image = models.ImageField(
        upload_to="mcq/imports/questions/images/",
        blank=True,
        null=True,
        storage=STAGING_FILE_STORAGE,
    )

    question_audio = models.FileField(
        upload_to="mcq/imports/questions/audio/",
        blank=True,
        null=True,
        storage=STAGING_FILE_STORAGE,
    )
    # --------------------------------------------------------
    # Legacy text option fields
    #
    # Kept for compatibility with the existing migration/data.
    # New imports will use ImportedOption below.
    # --------------------------------------------------------

    option_a = models.TextField(
        blank=True,
    )

    option_b = models.TextField(
        blank=True,
    )

    option_c = models.TextField(
        blank=True,
    )

    option_d = models.TextField(
        blank=True,
    )

    correct_answer = models.CharField(
        max_length=1,
        blank=True,
    )

    needs_review = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.import_job.name} - "
            f"Q{self.question_number}"
        )


class ImportedOption(models.Model):
    """
    One answer option belonging to an imported question.

    Unlike the old option_a/option_b/option_c/option_d
    fields, this supports any number of options and allows
    each option to contain text, an image, audio, or a
    combination of these.
    """

    imported_question = models.ForeignKey(
        ImportedQuestion,
        on_delete=models.CASCADE,
        related_name="options",
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    text = models.TextField(
        blank=True,
    )

    image = models.ImageField(
        upload_to="mcq/imports/options/images/",
        blank=True,
        null=True,
        storage=STAGING_FILE_STORAGE,
    )

    audio = models.FileField(
        upload_to="mcq/imports/options/audio/",
        blank=True,
        null=True,
        storage=STAGING_FILE_STORAGE,
    )

    is_correct = models.BooleanField(
        default=False,
    )

    needs_review = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "order",
            "id",
        ]

    def __str__(self):
        return (
            f"Q{self.imported_question.question_number} "
            f"- Option {self.order}"
        )