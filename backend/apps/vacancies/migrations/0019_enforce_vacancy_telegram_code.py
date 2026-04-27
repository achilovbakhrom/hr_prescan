import secrets

from django.db import migrations, models
from django.db.models import Q


def _next_code(existing_codes: set[int]) -> int:
    for _ in range(1000):
        code = 100000 + secrets.randbelow(900000)
        if code not in existing_codes:
            existing_codes.add(code)
            return code
    raise RuntimeError("Could not generate a unique Telegram vacancy code")


def backfill_invalid_telegram_codes(apps, schema_editor):
    Vacancy = apps.get_model("vacancies", "Vacancy")
    valid_code_filter = Q(telegram_code__gte=100000, telegram_code__lte=999999)
    existing_codes = set(Vacancy.objects.filter(valid_code_filter).values_list("telegram_code", flat=True))

    vacancies = Vacancy.objects.filter(
        Q(telegram_code__isnull=True) | Q(telegram_code__lt=100000) | Q(telegram_code__gt=999999),
    ).only("id", "telegram_code")
    for vacancy in vacancies.iterator():
        Vacancy.objects.filter(pk=vacancy.pk).update(
            telegram_code=_next_code(existing_codes),
        )


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0018_shift_criteria_order_to_one_based"),
    ]

    operations = [
        migrations.RunPython(backfill_invalid_telegram_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="vacancy",
            name="telegram_code",
            field=models.PositiveIntegerField(blank=True, unique=True),
        ),
        migrations.AddConstraint(
            model_name="vacancy",
            constraint=models.CheckConstraint(
                condition=models.Q(telegram_code__gte=100000, telegram_code__lte=999999),
                name="vacancy_telegram_code_6_digits",
            ),
        ),
    ]
