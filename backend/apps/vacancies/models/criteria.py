from django.db import models

from apps.common.models import BaseModel


class ScreeningStep(models.TextChoices):
    """Shared choices for prescanning vs interview step."""

    PRESCANNING = "prescanning", "Prescanning"
    INTERVIEW = "interview", "Interview"


class VacancyCriteria(BaseModel):
    """Evaluation criteria for scoring candidates."""

    vacancy = models.ForeignKey(
        "vacancies.Vacancy",
        on_delete=models.CASCADE,
        related_name="criteria",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    weight = models.IntegerField(default=1)
    is_default = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    step = models.CharField(
        max_length=15,
        choices=ScreeningStep.choices,
        default=ScreeningStep.PRESCANNING,
    )
    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = "vacancies"
        verbose_name_plural = "vacancy criteria"
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.name} (weight={self.weight})"


class InterviewQuestion(BaseModel):
    """Interview questions for a vacancy."""

    class Source(models.TextChoices):
        AI_GENERATED = "ai_generated", "AI Generated"
        HR_ADDED = "hr_added", "HR Added"

    vacancy = models.ForeignKey(
        "vacancies.Vacancy",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.AI_GENERATED,
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    step = models.CharField(
        max_length=15,
        choices=ScreeningStep.choices,
        default=ScreeningStep.PRESCANNING,
    )
    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = "vacancies"
        ordering = ["order"]

    def __str__(self) -> str:
        return f"Q{self.order}: {self.text[:60]}"
