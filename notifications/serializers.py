from rest_framework import serializers

from .models import Notification, NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["created_at", "user"]


class PublishNotificationSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
    )

    send_to_all_students = serializers.BooleanField(
        required=False,
        default=False,
    )

    title = serializers.CharField(
        max_length=255,
    )

    message = serializers.CharField()

    notification_type = serializers.ChoiceField(
        choices=Notification.Type.choices,
        default=Notification.Type.INFO,
    )

    def validate(self, attrs):
        user_ids = attrs.get("user_ids", [])
        send_to_all_students = attrs.get("send_to_all_students", False)

        if not user_ids and not send_to_all_students:
            raise serializers.ValidationError(
                "Provide user_ids or set send_to_all_students to true."
            )

        return attrs