import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from cloudinary_storage.storage import VideoMediaCloudinaryStorage


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

    text = models.TextField(
        blank=True,
        help_text="Question text / prompt.",
    )

    image = models.ImageField(
        upload_to="mcq/questions/images/",
        blank=True,
        null=True,
    )

    audio = models.FileField(
        upload_to="mcq/questions/audio/",
        blank=True,
        null=True,
        storage=VideoMediaCloudinaryStorage(),
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
    )

    audio = models.FileField(
        upload_to="mcq/options/audio/",
        blank=True,
        null=True,
        storage=VideoMediaCloudinaryStorage(),
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