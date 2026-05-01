from uuid import uuid4

from django.utils import timezone

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancySource


def start_source_sync(*, source: ParsedVacancySource) -> ParsedVacancySource:
    if source.source_type not in (ParsedVacancySource.Type.HH_RU, ParsedVacancySource.Type.HH_UZ):
        raise ApplicationError("Only HeadHunter sources can be synced.")
    if not source.is_active:
        raise ApplicationError("Parsing is disabled for this source.")
    if source.sync_status in (
        ParsedVacancySource.SyncStatus.RUNNING,
        ParsedVacancySource.SyncStatus.STOPPING,
    ):
        raise ApplicationError("Parsing is already running for this source.")

    task_id = str(uuid4())
    source.sync_status = ParsedVacancySource.SyncStatus.RUNNING
    source.sync_task_id = task_id
    source.sync_error = ""
    source.sync_finished_at = None
    source.save(update_fields=["sync_status", "sync_task_id", "sync_error", "sync_finished_at", "updated_at"])
    from apps.job_parser.tasks import sync_parsed_vacancy_source_task

    sync_parsed_vacancy_source_task.apply_async(args=[str(source.id)], task_id=task_id)
    return source


def stop_source_sync(*, source: ParsedVacancySource) -> ParsedVacancySource:
    if source.sync_status not in (
        ParsedVacancySource.SyncStatus.RUNNING,
        ParsedVacancySource.SyncStatus.STOPPING,
    ):
        raise ApplicationError("Parsing is not running for this source.")

    if source.sync_task_id:
        from apps.job_parser.tasks import sync_parsed_vacancy_source_task

        sync_parsed_vacancy_source_task.app.control.revoke(source.sync_task_id)
    source.sync_status = ParsedVacancySource.SyncStatus.CANCELLED
    source.sync_finished_at = timezone.now()
    source.save(update_fields=["sync_status", "sync_finished_at", "updated_at"])
    return source
