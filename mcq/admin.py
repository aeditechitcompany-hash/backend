
from django.contrib import admin

from .models import (
    QuestionSet,
    MCQSection,
    Question,
    Option,
    Attempt,
    AttemptAnswer,
    MCQImport,
    ImportedQuestion,
    ImportedOption,
)


# --------------------------------------------------
# Regular MCQ Admin
# --------------------------------------------------

class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    show_change_link = True


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "question_count",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("category", "is_active")
    search_fields = ("title",)
    inlines = [QuestionInline]


@admin.register(MCQSection)
class MCQSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "question_set",
        "question_type",
        "points",
        "order",
    )
    list_filter = ("question_type", "question_set")
    inlines = [OptionInline]


admin.site.register(Option)


# --------------------------------------------------
# Attempts Admin
# --------------------------------------------------

class AttemptAnswerInline(admin.TabularInline):
    model = AttemptAnswer
    extra = 0


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "question_set",
        "status",
        "score",
        "max_score",
        "percentage",
        "passed",
    )
    list_filter = ("status", "passed", "question_set")
    inlines = [AttemptAnswerInline]


# --------------------------------------------------
# MCQ PDF Import Admin
# --------------------------------------------------

@admin.register(MCQImport)
class MCQImportAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "question_set",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("name",)


# Display imported options inside each question.
class ImportedOptionInline(admin.TabularInline):
    model = ImportedOption
    extra = 0
    fields = (
        "order",
        "text",
        "image",
        "audio",
        "is_correct",
        "needs_review",
    )


@admin.register(ImportedQuestion)
class ImportedQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "import_job",
        "question_number",
        "section",
        "question_preview",
        "option_count",
        "needs_review",
    )
    list_filter = (
        "import_job",
        "section",
        "needs_review",
    )
    search_fields = (
        "question_text",
        "import_job__name",
    )
    ordering = (
        "import_job__name",
        "question_number",
    )
    inlines = [ImportedOptionInline]

    @admin.display(description="Question")
    def question_preview(self, obj):
        return (
            obj.question_text or "[Image/audio question]"
        )[:100]

    @admin.display(description="Options")
    def option_count(self, obj):
        return obj.options.count()


# Display each imported option with its question number.
@admin.register(ImportedOption)
class ImportedOptionAdmin(admin.ModelAdmin):
    list_display = (
        "import_job_name",
        "question_number",
        "order",
        "text_preview",
        "is_correct",
        "needs_review",
    )
    list_filter = (
        "imported_question__import_job",
        "is_correct",
        "needs_review",
    )
    search_fields = (
        "text",
        "imported_question__question_text",
        "imported_question__import_job__name",
    )
    ordering = (
        "imported_question__import_job__name",
        "imported_question__question_number",
        "order",
    )

    @admin.display(
        description="Import job",
        ordering="imported_question__import_job__name",
    )
    def import_job_name(self, obj):
        return obj.imported_question.import_job.name

    @admin.display(
        description="Question number",
        ordering="imported_question__question_number",
    )
    def question_number(self, obj):
        return obj.imported_question.question_number

    @admin.display(description="Option text")
    def text_preview(self, obj):
        if obj.text:
            return obj.text[:80]
        if obj.image:
            return "[Image option]"
        if obj.audio:
            return "[Audio option]"
        return "[No text or media]"
