from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from .models import (
    ProcessStage,
    StudentProcess,
    ProcessStageHistory,
)


class StageHistoryInline(admin.TabularInline):
    model = ProcessStageHistory
    extra = 0
    readonly_fields = (
        "stage",
        "status",
        "completed_at",
        "updated_by",
    )


@admin.register(ProcessStage)
class ProcessStageAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "name",
        "description",
    )

    ordering = (
        "order",
    )


@admin.register(StudentProcess)
class StudentProcessAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "current_stage",
        "started_at",
        "updated_at",
    )

    list_filter = (
        "current_stage",
    )

    search_fields = (
        "student__user__email",
        "student__user__first_name",
        "student__user__last_name",
    )

    readonly_fields = (
        "started_at",
        "updated_at",
        "complete_stage_button",
    )

    fields = (
        "student",
        "current_stage",
        "started_at",
        "updated_at",
        "complete_stage_button",
    )

    inlines = [
        StageHistoryInline,
    ]

    # =========================================================
    # CUSTOM ADMIN URL
    # =========================================================

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<path:object_id>/complete-stage/",
                self.admin_site.admin_view(
                    self.complete_stage_view
                ),
                name="process_studentprocess_complete_stage",
            ),
        ]

        return custom_urls + urls

    # =========================================================
    # COMPLETE BUTTON
    # =========================================================

    @admin.display(
        description="Process Action"
    )
    def complete_stage_button(self, obj):

        if obj.current_stage is None:
            return mark_safe(
                '<span style="color:#777;">'
                'No current stage'
                '</span>'
            )

        return mark_safe(
            f'''
            <a href="{reverse(
                "admin:process_studentprocess_complete_stage",
                args=[obj.pk],
            )}"
            class="button"
            style="
                background:#198754;
                color:white;
                padding:10px 16px;
                border-radius:5px;
                text-decoration:none;
                display:inline-block;
                font-weight:600;
            ">
                ✓ Mark "{obj.current_stage.name}" Completed
            </a>
            '''
        )

    # =========================================================
    # COMPLETE STAGE VIEW
    # =========================================================

    def complete_stage_view(
        self,
        request,
        object_id,
    ):

        process = self.get_object(
            request,
            object_id,
        )

        if process is None:
            self.message_user(
                request,
                "Student process not found.",
                level=messages.ERROR,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:process_studentprocess_changelist",
                )
            )

        if process.current_stage is None:
            self.message_user(
                request,
                "This student has no current process stage.",
                level=messages.ERROR,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:process_studentprocess_change",
                    args=[object_id],
                )
            )

        # -----------------------------------------------------
        # ONLY ALLOW POST
        # -----------------------------------------------------

        if request.method != "POST":
            from django.shortcuts import render

            context = {
                **self.admin_site.each_context(request),
                "opts": self.model._meta,
                "original": process,
                "title": "Complete Process Stage",
                "current_stage": process.current_stage,
            }

            return render(
                request,
                "admin/process/studentprocess/complete_stage_confirm.html",
                context,
            )

        # -----------------------------------------------------
        # COMPLETE CURRENT STAGE
        # -----------------------------------------------------

        previous_stage = process.current_stage

        remarks = request.POST.get(
            "remarks",
            "",
        ).strip()

        try:
            result = process.complete_current_stage(
                updated_by=request.user,
                remarks=remarks,
            )

        except ValueError as exc:
            self.message_user(
                request,
                str(exc),
                level=messages.ERROR,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:process_studentprocess_change",
                    args=[object_id],
                )
            )

        # -----------------------------------------------------
        # SUCCESS MESSAGE
        # -----------------------------------------------------

        if result["finished"]:

            self.message_user(
                request,
                (
                    f'Stage "{previous_stage.name}" completed. '
                    f'The student has completed the entire process.'
                ),
                level=messages.SUCCESS,
            )

        else:

            self.message_user(
                request,
                (
                    f'Stage "{previous_stage.name}" completed. '
                    f'Student moved to '
                    f'"{result["current_stage"].name}".'
                ),
                level=messages.SUCCESS,
            )

        return HttpResponseRedirect(
            reverse(
                "admin:process_studentprocess_change",
                args=[object_id],
            )
        )