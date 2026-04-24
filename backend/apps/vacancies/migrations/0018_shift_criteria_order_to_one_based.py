from django.db import migrations
from django.db.models import F, Min


def shift_zero_based_criteria_order(apps, schema_editor):
    VacancyCriteria = apps.get_model("vacancies", "VacancyCriteria")
    groups = (
        VacancyCriteria.objects.values("vacancy_id", "step")
        .annotate(min_order=Min("order"))
        .filter(min_order=0)
    )

    for group in groups.iterator():
        VacancyCriteria.objects.filter(
            vacancy_id=group["vacancy_id"],
            step=group["step"],
        ).update(order=F("order") + 1)


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0017_backfill_vacancy_telegram_codes"),
    ]

    operations = [
        migrations.RunPython(shift_zero_based_criteria_order, migrations.RunPython.noop),
    ]
