import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0002_add_invitation_model"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Vacancy",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("requirements", models.TextField(blank=True)),
                ("responsibilities", models.TextField(blank=True)),
                ("skills", models.JSONField(default=list)),
                (
                    "salary_min",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
                ),
                (
                    "salary_max",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
                ),
                (
                    "salary_currency",
                    models.CharField(default="USD", max_length=3),
                ),
                ("location", models.CharField(blank=True, max_length=255)),
                ("is_remote", models.BooleanField(default=False)),
                (
                    "employment_type",
                    models.CharField(
                        choices=[
                            ("full_time", "Full Time"),
                            ("part_time", "Part Time"),
                            ("contract", "Contract"),
                            ("internship", "Internship"),
                        ],
                        default="full_time",
                        max_length=20,
                    ),
                ),
                (
                    "experience_level",
                    models.CharField(
                        choices=[
                            ("junior", "Junior"),
                            ("middle", "Middle"),
                            ("senior", "Senior"),
                            ("lead", "Lead"),
                            ("director", "Director"),
                        ],
                        default="middle",
                        max_length=20,
                    ),
                ),
                ("deadline", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("paused", "Paused"),
                            ("closed", "Closed"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                (
                    "visibility",
                    models.CharField(
                        choices=[
                            ("public", "Public"),
                            ("private", "Private"),
                        ],
                        default="public",
                        max_length=20,
                    ),
                ),
                (
                    "share_token",
                    models.UUIDField(default=uuid.uuid4, unique=True),
                ),
                ("interview_duration", models.IntegerField(default=30)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vacancies",
                        to="accounts.company",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_vacancies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "vacancies",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="VacancyCriteria",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("weight", models.IntegerField(default=1)),
                ("is_default", models.BooleanField(default=False)),
                ("order", models.IntegerField(default=0)),
                (
                    "vacancy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="criteria",
                        to="vacancies.vacancy",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "vacancy criteria",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="InterviewQuestion",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("text", models.TextField()),
                ("category", models.CharField(blank=True, max_length=100)),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("ai_generated", "AI Generated"),
                            ("hr_added", "HR Added"),
                        ],
                        default="ai_generated",
                        max_length=20,
                    ),
                ),
                ("order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "vacancy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="vacancies.vacancy",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
    ]
