import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from apps.common.models import BaseModel


class Vacancy(BaseModel):
    """A job vacancy posted by a company."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        PAUSED = "paused", "Paused"
        ARCHIVED = "archived", "Archived"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"

    class InterviewMode(models.TextChoices):
        CHAT = "chat", "Chat"
        MEET = "meet", "Meet"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full Time"
        PART_TIME = "part_time", "Part Time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"

    class ExperienceLevel(models.TextChoices):
        JUNIOR = "junior", "Junior"
        MIDDLE = "middle", "Middle"
        SENIOR = "senior", "Senior"
        LEAD = "lead", "Lead"
        DIRECTOR = "director", "Director"

    company = models.ForeignKey(
        "accounts.Company",
        on_delete=models.CASCADE,
        related_name="vacancies",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="created_vacancies",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    skills = models.JSONField(default=list)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default="USD")
    location = models.CharField(max_length=255, blank=True)
    is_remote = models.BooleanField(default=False)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.MIDDLE,
    )
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    share_token = models.UUIDField(unique=True, default=uuid.uuid4)
    interview_mode = models.CharField(
        max_length=10,
        choices=InterviewMode.choices,
        default=InterviewMode.CHAT,
    )
    interview_enabled = models.BooleanField(default=False)
    interview_duration = models.IntegerField(default=30)  # Meet mode only
    cv_required = models.BooleanField(default=False)
    company_info = models.TextField(blank=True, default="")  # Optional company description for AI interview intro
    prescanning_prompt = models.TextField(blank=True, default="")  # Additional instructions for prescanning AI agent
    interview_prompt = models.TextField(blank=True, default="")  # Additional instructions for interview AI agent
    employer = models.ForeignKey(
        "vacancies.EmployerCompany",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacancies",
    )
    is_deleted = models.BooleanField(default=False)
    keywords = models.JSONField(default=list, blank=True)  # AI-generated search keywords
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "vacancies"
        ordering = ["-created_at"]
        indexes = [
            GinIndex(fields=["search_vector"], name="vacancy_search_vector_gin"),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.company.name})"


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
    source = models.CharField(
        max_length=10,
        choices=Source.choices,
        default=Source.MANUAL,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class ScreeningStep(models.TextChoices):
    """Shared choices for prescanning vs interview step."""

    PRESCANNING = "prescanning", "Prescanning"
    INTERVIEW = "interview", "Interview"


class VacancyCriteria(BaseModel):
    """Evaluation criteria for scoring candidates."""

    vacancy = models.ForeignKey(
        Vacancy,
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

    class Meta:
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
        Vacancy,
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

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"Q{self.order}: {self.text[:60]}"
