from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vacancies", "0009_employercompany_vacancy_employer"),
    ]

    operations = [
        migrations.AddField(
            model_name="vacancy",
            name="prescanning_language",
            field=models.CharField(
                choices=[("en", "English"), ("ru", "Russian"), ("uz", "Uzbek")],
                default="en",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="employercompany",
            name="description_translations",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
