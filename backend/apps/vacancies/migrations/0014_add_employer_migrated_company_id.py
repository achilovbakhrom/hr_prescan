from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0013_vacancy_translation_fields"),
    ]

    operations = [
        # Scratch column used by 0015 to map EmployerCompany rows to the new Company rows.
        # Dropped in 0016 along with the EmployerCompany model.
        migrations.AddField(
            model_name="employercompany",
            name="migrated_company_id",
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
    ]
