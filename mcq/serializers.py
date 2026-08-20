from rest_framework import serializers

from .models import (
    QuestionSet,
    Question,
    Option,
    Attempt,
    AttemptAnswer,
)


# ============================================================
# OPTION
# ============================================================

class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option

        fields = [
            "id",
            "question",
            "text",
            "image",
            "audio",
            "order",
            "is_correct",
        ]


# ============================================================
# OPTION PUBLIC
#
# Used by STUDENTS.
#
# IMPORTANT:
# is_correct is intentionally NOT included.
# ============================================================

class OptionPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option

        fields = [
            "id",
            "text",
            "image",
            "audio",
            "order",
        ]


# ============================================================
# QUESTION
#
# Admin / backend serializer
# ============================================================

class QuestionSerializer(serializers.ModelSerializer):

    options = OptionSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Question

        fields = [
            "id",
            "question_set",
            "question_type",
            "text",
            "image",
            "audio",
            "explanation",
            "points",
            "order",
            "created_at",
            "options",
        ]


# ============================================================
# QUESTION PUBLIC
#
# Used by STUDENTS.
#
# IMPORTANT:
# - is_correct is NOT included
# - explanation is NOT included
# ============================================================

class QuestionPublicSerializer(serializers.ModelSerializer):

    options = OptionPublicSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Question

        fields = [
            "id",
            "question_type",
            "text",
            "image",
            "audio",
            "points",
            "order",
            "options",
        ]


# ============================================================
# QUESTION SET
#
# Basic question-set information.
# ============================================================

class QuestionSetSerializer(serializers.ModelSerializer):

    question_count = serializers.ReadOnlyField()

    class Meta:
        model = QuestionSet

        fields = [
            "id",
            "title",
            "description",
            "category",
            "time_limit_minutes",
            "passing_score_percentage",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
            "question_count",
        ]

        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]


# ============================================================
# QUESTION SET DETAIL
#
# Admin / detailed view.
#
# Includes correct answers.
# ============================================================

class QuestionSetDetailSerializer(
    QuestionSetSerializer
):

    questions = QuestionSerializer(
        many=True,
        read_only=True,
    )

    class Meta(QuestionSetSerializer.Meta):

        fields = (
            QuestionSetSerializer.Meta.fields
            + ["questions"]
        )


# ============================================================
# QUESTION SET TAKE
#
# Student quiz view.
#
# IMPORTANT:
# Student does NOT receive correct answers.
# ============================================================

class QuestionSetTakeSerializer(
    QuestionSetSerializer
):

    questions = QuestionPublicSerializer(
        many=True,
        read_only=True,
    )

    class Meta(QuestionSetSerializer.Meta):

        fields = (
            QuestionSetSerializer.Meta.fields
            + ["questions"]
        )


# ============================================================
# ATTEMPT ANSWER
# ============================================================

class AttemptAnswerSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = AttemptAnswer

        fields = [
            "id",
            "attempt",
            "question",
            "selected_option",
            "is_correct",
            "answered_at",
        ]

        read_only_fields = [
            "is_correct",
            "answered_at",
        ]


# ============================================================
# ATTEMPT
# ============================================================

class AttemptSerializer(
    serializers.ModelSerializer
):

    answers = AttemptAnswerSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Attempt

        fields = [
            "id",
            "student",
            "question_set",
            "status",
            "started_at",
            "submitted_at",
            "score",
            "max_score",
            "percentage",
            "passed",
            "answers",
        ]

        read_only_fields = [
            "student",
            "started_at",
            "submitted_at",
            "score",
            "max_score",
            "percentage",
            "passed",
        ]


# ============================================================
# SUBMIT ANSWER
# ============================================================

class SubmitAnswerSerializer(
    serializers.Serializer
):

    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(),
    )

    selected_option = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):

        question = attrs["question"]
        selected_option = attrs.get("selected_option")

        if selected_option is not None:
            if selected_option.question_id != question.id:
                raise serializers.ValidationError({
                    "selected_option": (
                        "Selected option does not belong "
                        "to the selected question."
                    )
                })

        return attrs