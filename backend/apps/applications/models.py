import uuid

from django.db import models

from apps.common.models import BaseModel


class Application(BaseModel):
    """A candidate's application to a vacancy."""

    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        PRESCANNED = "prescanned", "Prescanned"
        INTERVIEWED = "interviewed", "Interviewed"
        SHORTLISTED = "shortlisted", "Shortlisted"
        HIRED = "hired", "Hired"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"
        ARCHIVED = "archived", "Archived"

    vacancy = models.ForeignKey(
        "vacancies.Vacancy",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    candidate = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )

    # Candidate info (always required, even without account)
    candidate_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()
    candidate_phone = models.CharField(max_length=50, blank=True, default="")

    # CV
    cv_file = models.CharField(max_length=500, blank=True, default="")  # MinIO path
    cv_original_filename = models.CharField(max_length=255, blank=True, default="")

    # AI-parsed data (populated by Celery tasks)
    cv_parsed_text = models.TextField(blank=True, default="")  # raw extracted text
    cv_parsed_data = models.JSONField(default=dict, blank=True)  # structured: skills, experience, education
    match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )  # 0-100
    match_details = models.JSONField(default=dict, blank=True)  # per-criteria match breakdown
    match_notes_translations = models.JSONField(default=dict, blank=True)
    cv_summary_translations = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.APPLIED,
    )
    is_deleted = models.BooleanField(default=False)  # soft delete (cleared from archive)
    hr_notes = models.TextField(blank=True, default="")
    hiring_manager_token = models.UUIDField(unique=True, default=uuid.uuid4)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["vacancy", "candidate_email"],
                name="unique_application_per_vacancy",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.candidate_name} -> {self.vacancy.title}"


class HiringManagerFeedback(BaseModel):
    """Feedback submitted from a read-only candidate review link."""

    class Recommendation(models.TextChoices):
        ADVANCE = "advance", "Advance"
        MAYBE = "maybe", "Maybe"
        REJECT = "reject", "Reject"

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="hiring_manager_feedback",
    )
    reviewer_name = models.CharField(max_length=255)
    reviewer_role = models.CharField(max_length=255, blank=True, default="")
    recommendation = models.CharField(max_length=20, choices=Recommendation.choices)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.reviewer_name} feedback for {self.application_id}"


class ApplicationEvent(BaseModel):
    """Audit event for candidate collaboration actions."""

    class EventType(models.TextChoices):
        SHARE_LINK_ROTATED = "share_link_rotated", "Share Link Rotated"
        HIRING_MANAGER_FEEDBACK = "hiring_manager_feedback", "Hiring Manager Feedback"

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="events",
    )
    event_type = models.CharField(max_length=50, choices=EventType.choices)
    actor_name = models.CharField(max_length=255, blank=True, default="")
    message = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_type} for {self.application_id}"


class HRCandidate(BaseModel):
    """Deduplicated candidate record for an HR account."""

    account_owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="hr_candidates",
    )
    candidate = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hr_candidate_records",
    )
    candidate_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()
    candidate_email_normalized = models.CharField(max_length=254)
    candidate_phone = models.CharField(max_length=50, blank=True, default="")
    latest_application = models.ForeignKey(
        Application,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    notes = models.TextField(blank=True, default="")
    first_seen_at = models.DateTimeField()
    last_activity_at = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-last_activity_at"]
        indexes = [
            models.Index(fields=["account_owner", "candidate_email_normalized"]),
            models.Index(fields=["account_owner", "last_activity_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["account_owner", "candidate_email_normalized"],
                condition=models.Q(is_deleted=False),
                name="unique_active_hr_candidate_email_per_account",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.candidate_name} ({self.candidate_email})"
