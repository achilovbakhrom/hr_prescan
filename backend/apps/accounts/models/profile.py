import uuid

from django.db import models


class CandidateProfile(models.Model):
    """Extended profile data for candidates (CV builder)."""

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full Time"
        PART_TIME = "part_time", "Part Time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )
    headline = models.CharField(max_length=255, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    date_of_birth = models.DateField(null=True, blank=True)
    linkedin_url = models.URLField(max_length=500, blank=True, default="")
    github_url = models.URLField(max_length=500, blank=True, default="")
    website_url = models.URLField(max_length=500, blank=True, default="")

    desired_salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    desired_salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    desired_salary_currency = models.CharField(max_length=3, default="USD")
    desired_salary_negotiable = models.BooleanField(default=False)
    desired_employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        blank=True,
        default="",
    )
    is_open_to_work = models.BooleanField(default=False)
    share_token = models.CharField(max_length=64, unique=True, blank=True, default="")

    skills = models.ManyToManyField("common.Skill", blank=True, related_name="candidate_profiles")
    photo = models.CharField(max_length=500, blank=True, default="")  # MinIO path

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"

    def __str__(self) -> str:
        return f"Profile: {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.share_token:
            import secrets

            self.share_token = secrets.token_urlsafe(24)
        super().save(*args, **kwargs)


class WorkExperience(models.Model):
    """Work experience entry in a candidate's CV."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="work_experiences",
    )
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    employment_type = models.CharField(
        max_length=20,
        choices=CandidateProfile.EmploymentType.choices,
        blank=True,
        default="",
    )
    location = models.CharField(max_length=255, blank=True, default="")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, default="")
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-is_current", "-start_date"]

    def __str__(self) -> str:
        return f"{self.position} at {self.company_name}"


class Education(models.Model):
    """Education entry in a candidate's CV."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="educations",
    )
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, blank=True, default="")
    education_level = models.ForeignKey(
        "common.EducationLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    field_of_study = models.CharField(max_length=255, blank=True, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-end_date"]

    def __str__(self) -> str:
        return f"{self.degree} at {self.institution}"


class CandidateLanguage(models.Model):
    """Language proficiency entry in a candidate's CV."""

    class Proficiency(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        ELEMENTARY = "elementary", "Elementary"
        INTERMEDIATE = "intermediate", "Intermediate"
        UPPER_INTERMEDIATE = "upper_intermediate", "Upper Intermediate"
        ADVANCED = "advanced", "Advanced"
        NATIVE = "native", "Native"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="languages",
    )
    language = models.ForeignKey("common.Language", on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=Proficiency.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "language"],
                name="unique_candidate_language",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.language.name} ({self.proficiency})"


class Certification(models.Model):
    """Certification entry in a candidate's CV."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="certifications",
    )
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255, blank=True, default="")
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(max_length=500, blank=True, default="")
    image = models.CharField(max_length=500, blank=True, default="")  # MinIO path
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-issue_date"]

    def __str__(self) -> str:
        return self.name


class CandidateCV(models.Model):
    """Generated CV PDF. One candidate can have multiple CVs, only one active."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="cvs",
    )
    name = models.CharField(max_length=255, default="My CV")
    template = models.CharField(max_length=50, default="classic")
    file = models.CharField(max_length=500, blank=True, default="")  # MinIO path
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-is_active", "-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"

    def activate(self):
        """Activate this CV and deactivate all others for the same profile."""
        CandidateCV.objects.filter(profile=self.profile, is_active=True).update(is_active=False)
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
