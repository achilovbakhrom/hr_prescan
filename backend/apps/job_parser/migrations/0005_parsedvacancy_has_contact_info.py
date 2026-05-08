from django.db import migrations, models


def populate_has_contact_info(apps, schema_editor):
    from apps.job_parser.services.contact_detection import parsed_vacancy_has_contact_info

    ParsedVacancy = apps.get_model("job_parser", "ParsedVacancy")
    updates = []
    for vacancy in ParsedVacancy.objects.only(
        "id",
        "description",
        "requirements",
        "responsibilities",
        "raw_payload",
        "has_contact_info",
    ).iterator(chunk_size=500):
        has_contact_info = parsed_vacancy_has_contact_info(vacancy)
        if vacancy.has_contact_info != has_contact_info:
            vacancy.has_contact_info = has_contact_info
            updates.append(vacancy)
        if len(updates) >= 500:
            ParsedVacancy.objects.bulk_update(updates, ["has_contact_info"])
            updates.clear()
    if updates:
        ParsedVacancy.objects.bulk_update(updates, ["has_contact_info"])


class Migration(migrations.Migration):
    dependencies = [
        ("job_parser", "0004_source_sync_checkpoint"),
    ]

    operations = [
        migrations.AddField(
            model_name="parsedvacancy",
            name="has_contact_info",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.RunPython(populate_has_contact_info, migrations.RunPython.noop),
    ]
