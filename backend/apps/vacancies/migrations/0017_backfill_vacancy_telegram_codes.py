import secrets

from django.db import migrations


def _next_code(existing_codes: set[int]) -> int:
    for _ in range(1000):
        code = 100000 + secrets.randbelow(900000)
        if code not in existing_codes:
            existing_codes.add(code)
            return code
    raise RuntimeError("Could not generate a unique Telegram vacancy code")


def backfill_telegram_codes(apps, schema_editor):
    Vacancy = apps.get_model("vacancies", "Vacancy")
    existing_codes = set(
        Vacancy.objects.exclude(telegram_code__isnull=True).values_list("telegram_code", flat=True)
    )

    vacancies = Vacancy.objects.filter(telegram_code__isnull=True).only("id", "telegram_code")
    for vacancy in vacancies.iterator():
        Vacancy.objects.filter(pk=vacancy.pk, telegram_code__isnull=True).update(
            telegram_code=_next_code(existing_codes),
        )


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0016_drop_vacancy_employer_and_employer_model"),
    ]

    operations = [
        migrations.RunPython(backfill_telegram_codes, migrations.RunPython.noop),
    ]
