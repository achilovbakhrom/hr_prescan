import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("vacancies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
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
                ("candidate_name", models.CharField(max_length=255)),
                ("candidate_email", models.EmailField(max_length=254)),
                (
                    "candidate_phone",
                    models.CharField(blank=True, default="", max_length=50),
                ),
                (
                    "cv_file",
                    models.CharField(blank=True, default="", max_length=500),
                ),
                (
                    "cv_original_filename",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "cv_parsed_text",
                    models.TextField(blank=True, default=""),
                ),
                (
                    "cv_parsed_data",
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    "match_score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                    ),
                ),
                (
                    "match_details",
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("applied", "Applied"),
                            ("interview_scheduled", "Interview Scheduled"),
                            ("interview_in_progress", "Interview In Progress"),
                            ("interview_completed", "Interview Completed"),
                            ("reviewing", "Reviewing"),
                            ("shortlisted", "Shortlisted"),
                            ("rejected", "Rejected"),
                        ],
                        default="applied",
                        max_length=30,
                    ),
                ),
                ("hr_notes", models.TextField(blank=True, default="")),
                (
                    "candidate",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vacancy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="vacancies.vacancy",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.UniqueConstraint(
                fields=("vacancy", "candidate_email"),
                name="unique_application_per_vacancy",
            ),
        ),
    ]
