from django.contrib import admin
from .models import DocumentType, Document

admin.site.register(DocumentType)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("student", "document_type", "status", "uploaded_at", "reviewed_by")
    list_filter = ("status", "document_type")
    search_fields = ("student__user__email",)
