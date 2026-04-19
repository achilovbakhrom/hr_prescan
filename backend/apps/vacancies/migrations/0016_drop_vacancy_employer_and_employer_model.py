from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0015_migrate_employers_to_companies"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vacancy",
            name="employer",
        ),
        migrations.DeleteModel(
            name="EmployerCompany",
        ),
    ]
