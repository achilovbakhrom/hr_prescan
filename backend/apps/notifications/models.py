from django.db import models

from apps.common.models import BaseModel


class Notification(BaseModel):
    """In-app notification for a user."""

    class Type(models.TextChoices):
        APPLICATION_RECEIVED = "application_received", "Application Received"
        INTERVIEW_SCHEDULED = "interview_scheduled", "Interview Scheduled"
        INTERVIEW_COMPLETED = "interview_completed", "Interview Completed"
        INTERVIEW_REMINDER = "interview_reminder", "Interview Reminder"
        STATUS_CHANGED = "status_changed", "Status Changed"
        INVITATION_RECEIVED = "invitation_received", "Invitation Received"
        DIRECT_MESSAGE = "direct_message", "Direct Message"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.type} for {self.user_id}: {self.title}"


class Message(BaseModel):
    """Direct message between HR and candidate."""

    class DeliveryChannel(models.TextChoices):
        WEB = "web", "Web"
        TELEGRAM = "telegram", "Telegram"

    class DeliveryStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    sender = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    recipient = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    application = models.ForeignKey(
        "applications.Application",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messages",
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    delivery_channel = models.CharField(
        max_length=20,
        choices=DeliveryChannel.choices,
        default=DeliveryChannel.WEB,
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
    )
    delivered_at = models.DateTimeField(null=True, blank=True)
    telegram_message_id = models.CharField(max_length=64, blank=True, default="")
    delivery_failure_reason = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Message from {self.sender_id} to {self.recipient_id}"
