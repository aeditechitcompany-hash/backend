from django.contrib import admin
from .models import QuestionSet, Question, Option, Attempt, AttemptAnswer


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    show_change_link = True


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "question_count", "is_active", "created_by", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("title",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "question_set", "question_type", "points", "order")
    list_filter = ("question_type", "question_set")
    inlines = [OptionInline]


admin.site.register(Option)


class AttemptAnswerInline(admin.TabularInline):
    model = AttemptAnswer
    extra = 0


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "question_set", "status", "score", "max_score", "percentage", "passed")
    list_filter = ("status", "passed", "question_set")
    inlines = [AttemptAnswerInline]

# Register your models here.
