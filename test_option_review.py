from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from mcq.models import MCQImport, ImportedOption

job = MCQImport.objects.get(pk=1)
option = ImportedOption.objects.filter(
    imported_question__import_job=job
).select_related("imported_question").order_by("id").first()

print("Import status:", job.status)
print("Option found:", option is not None)

if option is not None:
    print("Question ID:", option.imported_question_id)
    print("Option ID:", option.id)

    client = APIClient(HTTP_HOST="localhost")
    user = get_user_model().objects.get(email="nibangsh@app.com")
    client.force_authenticate(user=user)

    response = client.get(
        f"/api/mcq/imported-options/{option.id}/",
        HTTP_HOST="localhost",
    )
    print("GET status:", response.status_code)

    response = client.patch(
        f"/api/mcq/imported-options/{option.id}/",
        {"imported_question": option.imported_question_id},
        format="json",
        HTTP_HOST="localhost",
    )
    print("PATCH status:", response.status_code)

    option.refresh_from_db()
    print("Question ID unchanged:", option.imported_question_id)
    print("Needs review:", option.needs_review)
    print("Is correct:", option.is_correct)
