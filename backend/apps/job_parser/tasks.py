from celery import shared_task
from django.utils import timezone

from apps.job_parser.models import ParsedVacancySource
from apps.job_parser.services import refresh_telegram_actuality, sync_hh_source


@shared_task(bind=True, name="apps.job_parser.tasks.sync_parsed_vacancy_source")
def sync_parsed_vacancy_source_task(self, source_id: str) -> dict:
    source = ParsedVacancySource.objects.get(id=source_id, is_active=True)
    if (
        source.sync_task_id == self.request.id
        and source.sync_status == ParsedVacancySource.SyncStatus.CANCELLED
    ):
        return {"cancelled": True}
    source.sync_status = ParsedVacancySource.SyncStatus.RUNNING
    source.sync_task_id = self.request.id or source.sync_task_id
    source.sync_started_at = timezone.now()
    source.sync_finished_at = None
    source.sync_error = ""
    source.save(
        update_fields=[
            "sync_status",
            "sync_task_id",
            "sync_started_at",
            "sync_finished_at",
            "sync_error",
            "updated_at",
        ],
    )
    try:
        result = sync_hh_source(source=source)
    except Exception as exc:
        source.refresh_from_db(fields=["sync_status"])
        if source.sync_status in (
            ParsedVacancySource.SyncStatus.STOPPING,
            ParsedVacancySource.SyncStatus.CANCELLED,
        ):
            source.sync_status = ParsedVacancySource.SyncStatus.CANCELLED
            source.sync_error = ""
            result = {"cancelled": True}
        else:
            source.sync_status = ParsedVacancySource.SyncStatus.FAILED
            source.sync_error = str(exc)
            source.sync_finished_at = timezone.now()
            source.save(update_fields=["sync_status", "sync_error", "sync_finished_at", "updated_at"])
            raise
    else:
        source.refresh_from_db(fields=["sync_status"])
        source.sync_status = (
            ParsedVacancySource.SyncStatus.CANCELLED
            if source.sync_status
            in (
                ParsedVacancySource.SyncStatus.STOPPING,
                ParsedVacancySource.SyncStatus.CANCELLED,
            )
            else ParsedVacancySource.SyncStatus.SUCCEEDED
        )
    source.sync_finished_at = timezone.now()
    source.save(update_fields=["sync_status", "sync_finished_at", "updated_at"])
    return result


@shared_task(name="apps.job_parser.tasks.refresh_parsed_vacancy_actuality")
def refresh_parsed_vacancy_actuality_task() -> dict:
    return {"telegram_stale": refresh_telegram_actuality()}
