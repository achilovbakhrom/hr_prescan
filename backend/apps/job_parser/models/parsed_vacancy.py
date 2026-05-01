from django.db import models

from apps.common.models import BaseModel


class ParsedVacancySource(BaseModel):
    """External source configured by HR for vacancy parsing."""

    class Type(models.TextChoices):
        HH_RU = "hh_ru", "hh.ru"
        HH_UZ = "hh_uz", "hh.uz"
        TELEGRAM = "telegram", "Telegram"

    class SyncStatus(models.TextChoices):
        IDLE = "idle", "Idle"
        RUNNING = "running", "Running"
        STOPPING = "stopping", "Stopping"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    company = models.ForeignKey(
        "accounts.Company",
        on_delete=models.CASCADE,
        related_name="parsed_vacancy_sources",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="parsed_vacancy_sources",
    )
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=Type.choices)
    url = models.URLField(max_length=500, blank=True, default="")
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=False)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.IDLE)
    sync_task_id = models.CharField(max_length=255, blank=True, default="")
    sync_started_at = models.DateTimeField(null=True, blank=True)
    sync_finished_at = models.DateTimeField(null=True, blank=True)
    sync_error = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "source_type"]),
            models.Index(fields=["is_active", "last_synced_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_source_type_display()})"


class ParsedVacancy(BaseModel):
    """Normalized vacancy parsed from an external source before HR imports it."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        STALE = "stale", "Stale"
        EXPIRED = "expired", "Expired"
        CLOSED = "closed", "Closed"
        UNKNOWN = "unknown", "Unknown"
        DUPLICATE = "duplicate", "Duplicate"
        IMPORTED = "imported", "Imported"

    source = models.ForeignKey(
        ParsedVacancySource,
        on_delete=models.CASCADE,
        related_name="vacancies",
    )
    external_id = models.CharField(max_length=255)
    external_url = models.URLField(max_length=500, blank=True, default="")
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    requirements = models.TextField(blank=True, default="")
    responsibilities = models.TextField(blank=True, default="")
    skills = models.JSONField(default=list, blank=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default="USD")
    location = models.CharField(max_length=255, blank=True, default="")
    employment_type = models.CharField(max_length=20, blank=True, default="")
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNKNOWN)
    actuality_reason = models.CharField(max_length=255, blank=True, default="")
    raw_payload = models.JSONField(default=dict, blank=True)
    fingerprint = models.CharField(max_length=64, db_index=True)
    imported_vacancy = models.ForeignKey(
        "vacancies.Vacancy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parsed_sources",
    )

    class Meta:
        ordering = ["-published_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["source", "external_id"], name="unique_parsed_vacancy_per_source"),
        ]
        indexes = [
            models.Index(fields=["source", "status"]),
            models.Index(fields=["status", "last_seen_at"]),
            models.Index(fields=["fingerprint"]),
        ]

    def __str__(self) -> str:
        return self.title
