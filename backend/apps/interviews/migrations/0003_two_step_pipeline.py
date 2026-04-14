"""Convert Interview from OneToOne to ForeignKey and add session_type.

- Change application field from OneToOneField to ForeignKey
- Add session_type field (prescanning or interview)
- Set all existing records to prescanning
"""

import django.db.models.deletion
from django.db import migrations, models


def set_existing_session_type(apps, schema_editor):
    """Set all existing interview records to prescanning session type."""
    Interview = apps.get_model("interviews", "Interview")
    Interview.objects.all().update(session_type="prescanning")


class Migration(migrations.Migration):
    dependencies = [
        ("interviews", "0002_alter_interview_options_and_more"),
        ("applications", "0002_alter_application_status"),
    ]

    operations = [
        # Change OneToOneField to ForeignKey
        migrations.AlterField(
            model_name="interview",
            name="application",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sessions",
                to="applications.application",
            ),
        ),
        # Add session_type field
        migrations.AddField(
            model_name="interview",
            name="session_type",
            field=models.CharField(
                choices=[("prescanning", "Prescanning"), ("interview", "Interview")],
                default="prescanning",
                max_length=15,
            ),
        ),
        # Update default for screening_mode from MEET to CHAT
        migrations.AlterField(
            model_name="interview",
            name="screening_mode",
            field=models.CharField(
                choices=[("chat", "Chat"), ("meet", "Meet")],
                default="chat",
                max_length=10,
            ),
        ),
        # Data migration
        migrations.RunPython(
            set_existing_session_type,
            migrations.RunPython.noop,
        ),
    ]
