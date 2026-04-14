from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0006_vacancy_is_deleted"),
    ]

    operations = [
        TrigramExtension(),
    ]
