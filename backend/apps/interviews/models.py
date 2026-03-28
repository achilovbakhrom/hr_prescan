import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import BaseModel


class Interview(BaseModel):
    """AI screening session (prescanning or interview) linked to an application."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    class ScreeningMode(models.TextChoices):
        CHAT = "chat", "Chat"
        MEET = "meet", "Meet"

    class SessionType(models.TextChoices):
        PRESCANNING = "prescanning", "Prescanning"
        INTERVIEW = "interview", "Interview"

    application = models.ForeignKey(
        "applications.Application",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    session_type = models.CharField(
        max_length=15,
        choices=SessionType.choices,
        default=SessionType.PRESCANNING,
    )
    screening_mode = models.CharField(
        max_length=10,
        choices=ScreeningMode.choices,
        default=ScreeningMode.CHAT,
    )
    interview_token = models.UUIDField(unique=True, default=uuid.uuid4)
    duration_minutes = models.IntegerField(default=30)  # Meet mode only
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # LiveKit (Meet mode only)
    livekit_room_name = models.CharField(max_length=255, blank=True)
    candidate_token = models.CharField(max_length=500, blank=True)

    # Chat mode
    chat_history = models.JSONField(default=list)  # [{role, text, timestamp}]

    # Results (populated after interview)
    recording_path = models.CharField(max_length=500, blank=True)
    transcript = models.JSONField(default=list)
    overall_score = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
    )
    ai_summary = models.TextField(blank=True)
    language = models.CharField(
        max_length=10,
        choices=[("en", "English"), ("ru", "Russian"), ("uz", "Uzbek")],
        default="en",
    )
    ai_summary_translations = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.session_type} ({self.screening_mode}) for {self.application_id}"


class InterviewScore(BaseModel):
    """Per-criteria score from AI interview."""

    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name="scores",
    )
    criteria = models.ForeignKey(
        "vacancies.VacancyCriteria",
        on_delete=models.CASCADE,
        related_name="interview_scores",
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    ai_notes = models.TextField(blank=True)
    ai_notes_translations = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ["interview", "criteria"]

    def __str__(self) -> str:
        return f"Score {self.score}/10 for {self.criteria_id}"


class InterviewIntegrityFlag(BaseModel):
    """Anti-cheating flags detected during interview."""

    class FlagType(models.TextChoices):
        FACE_NOT_VISIBLE = "face_not_visible", "Face Not Visible"
        MULTIPLE_FACES = "multiple_faces", "Multiple Faces"
        GAZE_DEVIATION = "gaze_deviation", "Gaze Deviation"
        AUDIO_ANOMALY = "audio_anomaly", "Audio Anomaly"
        CV_INCONSISTENCY = "cv_inconsistency", "CV Inconsistency"
        SUSPICIOUS_TIMING = "suspicious_timing", "Suspicious Timing"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name="integrity_flags",
    )
    flag_type = models.CharField(
        max_length=30,
        choices=FlagType.choices,
    )
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
    )
    description = models.TextField()
    timestamp_seconds = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["timestamp_seconds"]

    def __str__(self) -> str:
        return f"{self.flag_type} ({self.severity})"
