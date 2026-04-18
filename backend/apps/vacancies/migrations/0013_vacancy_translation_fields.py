from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0012_telegram_channel_and_vacancy_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="vacancy",
            name="title_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="vacancy",
            name="description_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="vacancy",
            name="requirements_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="vacancy",
            name="responsibilities_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
