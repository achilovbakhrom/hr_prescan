from rest_framework import serializers

from apps.notifications.models import Message


class NotificationOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    data = serializers.JSONField()
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class MessageOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    sender_id = serializers.UUIDField()
    sender_name = serializers.SerializerMethodField()
    recipient_id = serializers.UUIDField()
    recipient_name = serializers.SerializerMethodField()
    application_id = serializers.UUIDField(allow_null=True)
    content = serializers.CharField()
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField()

    def get_sender_name(self, obj: Message) -> str:
        return obj.sender.full_name if hasattr(obj, "sender") and obj.sender else ""

    def get_recipient_name(self, obj: Message) -> str:
        return obj.recipient.full_name if hasattr(obj, "recipient") and obj.recipient else ""


class SendMessageInputSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000)


class SendCandidateEmailInputSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    body = serializers.CharField(max_length=10000)


class BulkStatusUpdateInputSerializer(serializers.Serializer):
    application_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100,
    )
    status = serializers.ChoiceField(choices=[
        ("reviewing", "Reviewing"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
    ])
