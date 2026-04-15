from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0005_add_hired_and_soft_delete"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="match_notes_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="application",
            name="cv_summary_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
