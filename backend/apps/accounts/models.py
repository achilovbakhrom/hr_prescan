import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Company(models.Model):
    """Company / tenant model."""

    class Size(models.TextChoices):
        SMALL = "small", "Small (1-50)"
        MEDIUM = "medium", "Medium (51-200)"
        LARGE = "large", "Large (201-1000)"
        ENTERPRISE = "enterprise", "Enterprise (1000+)"

    class SubscriptionStatus(models.TextChoices):
        TRIAL = "trial", "Trial"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    industries = models.ManyToManyField(
        "common.Industry",
        blank=True,
        related_name="companies",
    )
    size = models.CharField(max_length=20, choices=Size.choices)
    country = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # Subscription fields
    subscription_plan = models.ForeignKey(
        "subscriptions.SubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIAL,
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "companies"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):
    """Custom user manager using email as the unique identifier."""

    def create_user(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the username field."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        HR = "hr", "HR Manager"
        CANDIDATE = "candidate", "Candidate"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CANDIDATE)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    # Onboarding — False for new social auth users until they pick a role
    onboarding_completed = models.BooleanField(default=True)

    # Telegram integration
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    telegram_username = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class CandidateProfile(models.Model):
    """Extended profile data for candidates (CV builder)."""

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full Time"
        PART_TIME = "part_time", "Part Time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="candidate_profile",
    )
    headline = models.CharField(max_length=255, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    date_of_birth = models.DateField(null=True, blank=True)
    linkedin_url = models.URLField(max_length=500, blank=True, default="")
    github_url = models.URLField(max_length=500, blank=True, default="")
    website_url = models.URLField(max_length=500, blank=True, default="")

    desired_salary_min = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    desired_salary_max = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    desired_salary_currency = models.CharField(max_length=3, default="USD")
    desired_employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices, blank=True, default="",
    )
    is_open_to_work = models.BooleanField(default=True)

    skills = models.ManyToManyField("common.Skill", blank=True, related_name="candidate_profiles")
    photo = models.CharField(max_length=500, blank=True, default="")  # MinIO path

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile: {self.user.email}"


class WorkExperience(models.Model):
    """Work experience entry in a candidate's CV."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="work_experiences",
    )
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    employment_type = models.CharField(
        max_length=20, choices=CandidateProfile.EmploymentType.choices, blank=True, default="",
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
        ordering = ["-is_current", "-start_date"]

    def __str__(self) -> str:
        return f"{self.position} at {self.company_name}"


class Education(models.Model):
    """Education entry in a candidate's CV."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="educations",
    )
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, blank=True, default="")
    education_level = models.ForeignKey(
        "common.EducationLevel", on_delete=models.SET_NULL, null=True, blank=True,
    )
    field_of_study = models.CharField(max_length=255, blank=True, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
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
        CandidateProfile, on_delete=models.CASCADE, related_name="languages",
    )
    language = models.ForeignKey("common.Language", on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=Proficiency.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
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
        CandidateProfile, on_delete=models.CASCADE, related_name="certifications",
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
        ordering = ["-issue_date"]

    def __str__(self) -> str:
        return self.name


class CandidateCV(models.Model):
    """Generated CV PDF. One candidate can have multiple CVs, only one active."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="cvs",
    )
    name = models.CharField(max_length=255, default="My CV")
    template = models.CharField(max_length=50, default="classic")
    file = models.CharField(max_length=500, blank=True, default="")  # MinIO path
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"

    def activate(self):
        """Activate this CV and deactivate all others for the same profile."""
        CandidateCV.objects.filter(profile=self.profile, is_active=True).update(is_active=False)
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])


def _default_invitation_expiry() -> timezone.datetime:
    """Return default expiry: 7 days from now."""
    return timezone.now() + timedelta(days=7)


class Invitation(models.Model):
    """HR invitation to join a company."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    token = models.UUIDField(unique=True, default=uuid.uuid4)
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=_default_invitation_expiry)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "email"],
                condition=models.Q(is_accepted=False),
                name="unique_pending_invitation_per_company",
            ),
        ]

    def __str__(self) -> str:
        return f"Invitation for {self.email} to {self.company.name}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at
