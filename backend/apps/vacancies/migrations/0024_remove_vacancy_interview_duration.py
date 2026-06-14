from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0023_meet_only_interview_mode"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vacancy",
            name="interview_duration",
        ),
    ]
