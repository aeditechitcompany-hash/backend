from django.contrib import admin
from .models import StudentProfile, Education, Preferences


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    fields = ("degree_level", "institution_name", "gpa", "gpa_scale", "passout_year", "is_completed")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "country",
        "nationality",
        "assigned_counselor",
        "mcq_access",
        "book_access",
        "profile_completion_percentage",
    )

    list_filter = (
        "mcq_access",
        "book_access",
        "country",
        "nationality",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    inlines = [EducationInline]

    fieldsets = (
        (
            "Student Information",
            {
                "fields": (
                    "user",
                    "date_of_birth",
                    "gender",
                    "nationality",
                    "passport_number",
                    "address",
                    "city",
                    "country",
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "bio",
                    "profile_completion_percentage",
                    "assigned_counselor",
                )
            },
        ),
        (
            "Module Access",
            {
                "fields": (
                    "mcq_access",
                    "book_access",
                ),
            },
        ),
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("student", "degree_level", "institution_name", "gpa", "gpa_scale", "passout_year", "is_completed")
    list_filter = ("degree_level", "passout_year", "gpa_scale")
    search_fields = ("student__user__email", "institution_name")


@admin.register(Preferences)
class PreferencesAdmin(admin.ModelAdmin):
    list_display = ("student", "preferred_study_level", "preferred_intake", "budget_min", "budget_max")
    list_filter = ("preferred_study_level", "preferred_intake")
