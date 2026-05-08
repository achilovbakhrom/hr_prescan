from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0019_enforce_vacancy_telegram_code"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vacancy",
            name="deadline",
        ),
    ]
