from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from mcq.models import (
    ImportedOption,
    ImportedQuestion,
    MCQImport,
    QuestionSet,
)


class ImportedQuestionReviewAPITests(TestCase):
    """
    Tests for staged MCQ review safeguards.

    All records are created in Django's test database.
    The existing staged import is not referenced.
    """

    def setUp(self):
        User = get_user_model()

        self.staff_user = User.objects.create(
            username="staging_test_admin",
            email="staging_test_admin@example.com",
            password="unused-test-password",
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )

        self.regular_user = User.objects.create(
            username="staging_test_student",
            email="staging_test_student@example.com",
            password="unused-test-password",
            is_superuser=False,
            is_staff=False,
            is_active=True,
        )

        self.client = APIClient()

        self.question_set = QuestionSet.objects.create(
            title="Temporary staging review test set",
            is_active=True,
        )

        self.import_job = MCQImport.objects.create(
            name="Temporary staging review test",
            question_set=self.question_set,
            pdf="mcq/imports/staging-review-test.pdf",
            status="review",
        )

        self.question = ImportedQuestion.objects.create(
            import_job=self.import_job,
            question_number=1,
            section="reading",
            question_text="Which option is correct?",
            needs_review=True,
        )

        self.option_a = ImportedOption.objects.create(
            imported_question=self.question,
            order=1,
            text="Option A",
            is_correct=False,
            needs_review=True,
        )

        self.option_b = ImportedOption.objects.create(
            imported_question=self.question,
            order=2,
            text="Option B",
            is_correct=False,
            needs_review=True,
        )

        self.other_question = ImportedQuestion.objects.create(
            import_job=self.import_job,
            question_number=2,
            section="reading",
            question_text="A different question?",
            needs_review=True,
        )

        self.other_option = ImportedOption.objects.create(
            imported_question=self.other_question,
            order=1,
            text="Other question's option",
            is_correct=False,
            needs_review=True,
        )

    def authenticate_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)

    def test_non_staff_cannot_list_staged_questions_or_options(self):
        self.client.force_authenticate(user=self.regular_user)

        question_response = self.client.get(
            "/api/mcq/imported-questions/"
        )
        option_response = self.client.get(
            "/api/mcq/imported-options/"
        )

        self.assertEqual(question_response.status_code, 403)
        self.assertEqual(option_response.status_code, 403)

    def test_staff_can_list_staged_questions_and_options(self):
        self.authenticate_as_staff()

        question_response = self.client.get(
            "/api/mcq/imported-questions/"
        )
        option_response = self.client.get(
            "/api/mcq/imported-options/"
        )

        self.assertEqual(question_response.status_code, 200)
        self.assertEqual(option_response.status_code, 200)

    def test_option_cannot_be_moved_to_another_question(self):
        self.authenticate_as_staff()

        original_question_id = self.option_a.imported_question_id

        response = self.client.patch(
            f"/api/mcq/imported-options/{self.option_a.pk}/",
            {"imported_question": self.other_question.pk},
            format="json",
        )

        self.option_a.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            self.option_a.imported_question_id,
            original_question_id,
        )

    def test_correct_option_must_belong_to_target_question(self):
        self.authenticate_as_staff()

        response = self.client.post(
            f"/api/mcq/imported-questions/"
            f"{self.question.pk}/set-correct-option/",
            {"option_id": self.other_option.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(
            self.question.options.filter(is_correct=True).exists()
        )

        self.other_option.refresh_from_db()
        self.assertFalse(self.other_option.is_correct)

    def test_question_cannot_be_reviewed_without_correct_answer(self):
        self.authenticate_as_staff()

        response = self.client.post(
            f"/api/mcq/imported-questions/"
            f"{self.question.pk}/mark-reviewed/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.question.refresh_from_db()
        self.assertTrue(self.question.needs_review)

        self.assertTrue(
            self.question.options.filter(needs_review=True).exists()
        )

    def test_question_can_be_reviewed_after_selecting_correct_answer(self):
        self.authenticate_as_staff()

        correct_response = self.client.post(
            f"/api/mcq/imported-questions/"
            f"{self.question.pk}/set-correct-option/",
            {"option_id": self.option_a.pk},
            format="json",
        )

        self.assertEqual(correct_response.status_code, 200)

        self.option_a.refresh_from_db()
        self.option_b.refresh_from_db()

        self.assertTrue(self.option_a.is_correct)
        self.assertFalse(self.option_b.is_correct)

        review_response = self.client.post(
            f"/api/mcq/imported-questions/"
            f"{self.question.pk}/mark-reviewed/",
            {},
            format="json",
        )

        self.assertEqual(review_response.status_code, 200)

        self.question.refresh_from_db()
        self.option_a.refresh_from_db()
        self.option_b.refresh_from_db()

        self.assertFalse(self.question.needs_review)
        self.assertFalse(self.option_a.needs_review)
        self.assertFalse(self.option_b.needs_review)

        self.assertEqual(
            self.question.options.filter(is_correct=True).count(),
            1,
        )
