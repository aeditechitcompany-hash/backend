from django.contrib import admin
from .models import University, Course


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "ranking", "is_partner", "is_active")
    search_fields = ("name",)
    list_filter = ("is_partner", "is_active", "country")
    inlines = [CourseInline]


admin.site.register(Course)
