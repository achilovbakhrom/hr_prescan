"""Replace closed with archived in vacancy status choices.

Lifecycle: draft → published ↔ paused → archived
"""

from django.db import migrations, models


def migrate_closed_to_archived(apps, schema_editor):
    Vacancy = apps.get_model("vacancies", "Vacancy")
    Vacancy.objects.filter(status="closed").update(status="archived")


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0004_two_step_pipeline"),
    ]

    operations = [
        migrations.RunPython(migrate_closed_to_archived, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="vacancy",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("published", "Published"),
                    ("paused", "Paused"),
                    ("archived", "Archived"),
                ],
                default="draft",
                max_length=20,
            ),
        ),
    ]
