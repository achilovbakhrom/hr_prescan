"""Add hired status and is_deleted field for soft delete."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0004_add_archived_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.CharField(
                choices=[
                    ("applied", "Applied"),
                    ("prescanned", "Prescanned"),
                    ("interviewed", "Interviewed"),
                    ("shortlisted", "Shortlisted"),
                    ("hired", "Hired"),
                    ("rejected", "Rejected"),
                    ("expired", "Expired"),
                    ("archived", "Archived"),
                ],
                default="applied",
                max_length=30,
            ),
        ),
    ]
