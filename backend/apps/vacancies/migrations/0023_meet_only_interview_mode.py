from django.db import migrations, models


def set_vacancies_to_meet(apps, schema_editor):
    Vacancy = apps.get_model("vacancies", "Vacancy")
    Vacancy.objects.filter(interview_mode="chat").update(interview_mode="meet")


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0022_alter_vacancy_prescanning_language"),
    ]

    operations = [
        migrations.RunPython(set_vacancies_to_meet, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="vacancy",
            name="interview_mode",
            field=models.CharField(
                choices=[("meet", "Meet")],
                default="meet",
                max_length=10,
            ),
        ),
    ]
