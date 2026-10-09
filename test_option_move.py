from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from mcq.models import MCQImport, ImportedQuestion, ImportedOption

job = MCQImport.objects.get(pk=1)
option = ImportedOption.objects.filter(
    imported_question__import_job=job
).select_related("imported_question").order_by("id").first()

if option is None:
    print("STOP: No staged option exists.")
else:
    other_question = ImportedQuestion.objects.filter(
        import_job=job
    ).exclude(pk=option.imported_question_id).order_by("id").first()

    if other_question is None:
        print("STOP: No second staged question exists.")
    else:
        original_question_id = option.imported_question_id
        client = APIClient(HTTP_HOST="localhost")
        user = get_user_model().objects.get(email="nibangsh@app.com")
        client.force_authenticate(user=user)

        response = client.patch(
            f"/api/mcq/imported-options/{option.id}/",
            {"imported_question": other_question.id},
            format="json",
            HTTP_HOST="localhost",
        )

        option.refresh_from_db()
        print("PATCH move status:", response.status_code)
        print("Response:", response.data)
        print("Original question ID:", original_question_id)
        print("Question ID after request:", option.imported_question_id)
        print("Association unchanged:", option.imported_question_id == original_question_id)
