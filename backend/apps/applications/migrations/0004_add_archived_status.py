"""Add archived status to application choices."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0003_two_step_pipeline"),
    ]

    operations = [
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
                    ("archived", "Archived"),
                ],
                default="applied",
                max_length=30,
            ),
        ),
    ]
