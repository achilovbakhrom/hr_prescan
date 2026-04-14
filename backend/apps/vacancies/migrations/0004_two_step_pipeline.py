"""Add two-step screening pipeline fields to vacancy models.

- Rename screening_mode → interview_mode on Vacancy
- Add interview_enabled, prescanning_prompt, interview_prompt to Vacancy
- Add step field to VacancyCriteria and InterviewQuestion
"""

from django.db import migrations, models


def set_existing_steps_to_prescanning(apps, schema_editor):
    """Set all existing criteria and questions to prescanning step."""
    VacancyCriteria = apps.get_model("vacancies", "VacancyCriteria")
    InterviewQuestion = apps.get_model("vacancies", "InterviewQuestion")
    VacancyCriteria.objects.all().update(step="prescanning")
    InterviewQuestion.objects.all().update(step="prescanning")


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0003_add_company_info_to_vacancy"),
    ]

    operations = [
        # Rename screening_mode → interview_mode
        migrations.RenameField(
            model_name="vacancy",
            old_name="screening_mode",
            new_name="interview_mode",
        ),
        # Add new vacancy fields
        migrations.AddField(
            model_name="vacancy",
            name="interview_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="vacancy",
            name="prescanning_prompt",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="vacancy",
            name="interview_prompt",
            field=models.TextField(blank=True, default=""),
        ),
        # Add step field to VacancyCriteria
        migrations.AddField(
            model_name="vacancycriteria",
            name="step",
            field=models.CharField(
                choices=[("prescanning", "Prescanning"), ("interview", "Interview")],
                default="prescanning",
                max_length=15,
            ),
        ),
        # Add step field to InterviewQuestion
        migrations.AddField(
            model_name="interviewquestion",
            name="step",
            field=models.CharField(
                choices=[("prescanning", "Prescanning"), ("interview", "Interview")],
                default="prescanning",
                max_length=15,
            ),
        ),
        # Data migration
        migrations.RunPython(
            set_existing_steps_to_prescanning,
            migrations.RunPython.noop,
        ),
    ]
