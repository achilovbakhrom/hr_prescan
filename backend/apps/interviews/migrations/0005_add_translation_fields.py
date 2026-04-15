from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("interviews", "0004_interview_completed_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="interview",
            name="language",
            field=models.CharField(
                choices=[("en", "English"), ("ru", "Russian"), ("uz", "Uzbek")],
                default="en",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="interview",
            name="ai_summary_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="interviewscore",
            name="ai_notes_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
