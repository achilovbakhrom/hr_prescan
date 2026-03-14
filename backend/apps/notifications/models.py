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

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Message from {self.sender_id} to {self.recipient_id}"
