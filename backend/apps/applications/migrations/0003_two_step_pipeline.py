"""Update application statuses for two-step screening pipeline.

- Remove: interview_in_progress, interview_completed, reviewing
- Add: prescanned, interviewed
- Data migration: map old statuses to new ones
"""

from django.db import migrations, models


def migrate_statuses_forward(apps, schema_editor):
    """Map old application statuses to new ones."""
    Application = apps.get_model("applications", "Application")
    # interview_in_progress → applied (session tracks in-progress state)
    Application.objects.filter(status="interview_in_progress").update(status="applied")
    # interview_completed → prescanned
    Application.objects.filter(status="interview_completed").update(status="prescanned")
    # reviewing → prescanned
    Application.objects.filter(status="reviewing").update(status="prescanned")


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0002_alter_application_status"),
        ("interviews", "0003_two_step_pipeline"),
    ]

    operations = [
        # Data migration first (while old choices still valid at DB level)
        migrations.RunPython(
            migrate_statuses_forward,
            migrations.RunPython.noop,
        ),
        # Then alter the field choices
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.CharField(
                choices=[
                    ("applied", "Applied"),
                    ("prescanned", "Prescanned"),
                    ("interviewed", "Interviewed"),
                    ("shortlisted", "Shortlisted"),
                    ("rejected", "Rejected"),
                    ("expired", "Expired"),
                ],
                default="applied",
                max_length=30,
            ),
        ),
    ]
