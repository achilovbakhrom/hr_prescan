from django.db import models

from apps.common.models import BaseModel


class EmployerCompany(BaseModel):
    """A company that posts job vacancies. Belongs to a tenant Company."""

    class Source(models.TextChoices):
        MANUAL = "manual", "Manual"
        FILE = "file", "File"
        WEBSITE = "website", "Website"

    company = models.ForeignKey(
        "accounts.Company",
        on_delete=models.CASCADE,
        related_name="employers",
    )
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True)
    logo = models.URLField(blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    description_translations = models.JSONField(default=dict, blank=True)
    source = models.CharField(
        max_length=10,
        choices=Source.choices,
        default=Source.MANUAL,
    )

    class Meta:
        app_label = "vacancies"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
