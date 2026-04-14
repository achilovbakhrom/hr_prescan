import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("applications", "0001_initial"),
        ("vacancies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Interview",
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
                ("scheduled_at", models.DateTimeField()),
                ("duration_minutes", models.IntegerField(default=30)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                            ("no_show", "No Show"),
                        ],
                        default="scheduled",
                        max_length=20,
                    ),
                ),
                (
                    "livekit_room_name",
                    models.CharField(blank=True, max_length=255),
                ),
                (
                    "candidate_token",
                    models.CharField(blank=True, max_length=500),
                ),
                (
                    "recording_path",
                    models.CharField(blank=True, max_length=500),
                ),
                ("transcript", models.JSONField(default=list)),
                (
                    "overall_score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=4,
                        null=True,
                    ),
                ),
                ("ai_summary", models.TextField(blank=True)),
                (
                    "application",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interview",
                        to="applications.application",
                    ),
                ),
            ],
            options={
                "ordering": ["-scheduled_at"],
            },
        ),
        migrations.CreateModel(
            name="InterviewScore",
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
                (
                    "score",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                    ),
                ),
                ("ai_notes", models.TextField(blank=True)),
                (
                    "criteria",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interview_scores",
                        to="vacancies.vacancycriteria",
                    ),
                ),
                (
                    "interview",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scores",
                        to="interviews.interview",
                    ),
                ),
            ],
            options={
                "unique_together": {("interview", "criteria")},
            },
        ),
        migrations.CreateModel(
            name="InterviewIntegrityFlag",
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
                (
                    "flag_type",
                    models.CharField(
                        choices=[
                            ("face_not_visible", "Face Not Visible"),
                            ("multiple_faces", "Multiple Faces"),
                            ("gaze_deviation", "Gaze Deviation"),
                            ("audio_anomaly", "Audio Anomaly"),
                            ("cv_inconsistency", "CV Inconsistency"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                        ],
                        max_length=10,
                    ),
                ),
                ("description", models.TextField()),
                (
                    "timestamp_seconds",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "interview",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="integrity_flags",
                        to="interviews.interview",
                    ),
                ),
            ],
            options={
                "ordering": ["timestamp_seconds"],
            },
        ),
    ]
