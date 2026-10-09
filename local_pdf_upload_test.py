from pathlib import Path
import json
from types import SimpleNamespace
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from mcq.models import MCQImport, ImportedQuestion, ImportedOption

pdf_path = Path("Full set 1 F.pdf")
question_set_id = "3eb84de1-b5e9-43ad-8423-156f0a3b6eb8"

if not pdf_path.is_file():
    raise SystemExit(f"PDF not found: {pdf_path.resolve()}")

api = APIClient(HTTP_HOST="localhost")
api.raise_request_exception = False
api.force_authenticate(user=SimpleNamespace(
    is_authenticated=True,
    is_superuser=True,
    role="admin",
))

with pdf_path.open("rb") as f:
    pdf = SimpleUploadedFile(
        pdf_path.name, f.read(), content_type="application/pdf"
    )

    response = api.post(
        "/api/mcq/imports/upload/",
        {
            "pdf": pdf,
            "question_set": question_set_id,
            "name": "LOCAL PDF IMPORT TEST - DELETE LATER",
            "listening_start": "21",
            "listening_end": "40",
        },
        format="multipart",
    )

print("HTTP status:", response.status_code)
print("Response:", response.content.decode("utf-8", errors="replace"))

if response.status_code == 201:
    data = json.loads(response.content)
    job = MCQImport.objects.get(pk=data["id"])
    print("Import status:", job.status)
    print("Staged questions:", ImportedQuestion.objects.filter(import_job=job).count())
    print("Staged options:", ImportedOption.objects.filter(imported_question__import_job=job).count())
    print("Questions needing review:", ImportedQuestion.objects.filter(import_job=job, needs_review=True).count())
    print("Correct options selected:", ImportedOption.objects.filter(imported_question__import_job=job, is_correct=True).count())



