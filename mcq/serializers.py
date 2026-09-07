from rest_framework import serializers

from .models import (
    QuestionSet,
    Question,
    Option,
    Attempt,
    AttemptAnswer,
)


# ============================================================
# OPTION - ADMIN
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
# OPTION - PUBLIC / STUDENT
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
# QUESTION - ADMIN
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
# QUESTION - PUBLIC / STUDENT
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
# QUESTION SET - BASIC
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
# QUESTION SET - ADMIN DETAIL
#
# Includes correct answers and explanation.
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
            + [
                "questions",
            ]
        )


# ============================================================
# QUESTION SET - STUDENT TAKE
#
# IMPORTANT:
# Students do NOT receive:
# - is_correct
# - explanation
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
            + [
                "questions",
            ]
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

        selected_option = attrs.get(
            "selected_option"
        )

        if selected_option is not None:

            if selected_option.question_id != question.id:

                raise serializers.ValidationError({
                    "selected_option": (
                        "Selected option does not belong "
                        "to the selected question."
                    )
                })

        return attrs


# ============================================================
# LEADERBOARD
# ============================================================

class LeaderboardSerializer(
    serializers.Serializer
):

    rank = serializers.IntegerField()

    name = serializers.CharField()

    email = serializers.EmailField()

    score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    completed_quizzes = serializers.IntegerField()

    questions_solved = serializers.IntegerField()