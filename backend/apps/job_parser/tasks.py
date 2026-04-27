from celery import shared_task

from apps.job_parser.models import ParsedVacancySource
from apps.job_parser.services import refresh_telegram_actuality, sync_hh_source


@shared_task(name="apps.job_parser.tasks.sync_parsed_vacancy_source")
def sync_parsed_vacancy_source_task(source_id: str) -> dict:
    source = ParsedVacancySource.objects.get(id=source_id, is_active=True)
    return sync_hh_source(source=source)


@shared_task(name="apps.job_parser.tasks.refresh_parsed_vacancy_actuality")
def refresh_parsed_vacancy_actuality_task() -> dict:
    return {"telegram_stale": refresh_telegram_actuality()}
