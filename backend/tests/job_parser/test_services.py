from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from django.utils import timezone

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.job_parser.services import (
    import_parsed_vacancy,
    parse_telegram_job_message,
    refresh_telegram_actuality,
    start_source_sync,
    stop_source_sync,
    sync_hh_source,
    upsert_parsed_vacancy,
)
from apps.vacancies.models import Vacancy


def _source(company, hr_user, source_type=ParsedVacancySource.Type.HH_RU, *, is_active=True):
    return ParsedVacancySource.objects.create(
        company=company,
        created_by=hr_user,
        name="External jobs",
        source_type=source_type,
        settings={"text": "python"},
        is_active=is_active,
    )


class TestParsedVacancyCrud:
    def test_source_parsing_is_disabled_by_default(self, company, hr_user):
        source = ParsedVacancySource.objects.create(
            company=company,
            created_by=hr_user,
            name="Manual source",
            source_type=ParsedVacancySource.Type.HH_UZ,
        )

        assert source.is_active is False

    def test_upsert_parsed_vacancy_updates_seen_record(self, company, hr_user):
        source = _source(company, hr_user)
        parsed = upsert_parsed_vacancy(
            source=source,
            payload={"external_id": "42", "title": "Python Developer", "location": "Tashkent"},
        )

        updated = upsert_parsed_vacancy(
            source=source,
            payload={
                "external_id": "42",
                "title": "Senior Python Developer",
                "salary_min": "1000",
                "salary_currency": "usd",
            },
        )

        assert updated.id == parsed.id
        assert updated.title == "Senior Python Developer"
        assert updated.salary_min == 1000
        assert updated.salary_currency == "USD"
        assert updated.last_seen_at is not None

    def test_import_parsed_vacancy_creates_private_draft(self, company, hr_user):
        source = _source(company, hr_user)
        parsed = upsert_parsed_vacancy(
            source=source,
            payload={
                "external_id": "55",
                "title": "Data Analyst",
                "description": "Analyze product metrics",
                "skills": ["SQL", "SQL", "Python"],
                "location": "Remote",
            },
        )

        vacancy = import_parsed_vacancy(parsed_vacancy=parsed, created_by=hr_user)
        parsed.refresh_from_db()

        assert vacancy.status == Vacancy.Status.DRAFT
        assert vacancy.visibility == Vacancy.Visibility.PRIVATE
        assert vacancy.company == company
        assert vacancy.skills == ["SQL", "Python"]
        assert parsed.status == ParsedVacancy.Status.IMPORTED
        assert parsed.imported_vacancy == vacancy

    def test_import_rejects_closed_vacancy(self, company, hr_user):
        source = _source(company, hr_user)
        parsed = upsert_parsed_vacancy(
            source=source,
            payload={"external_id": "99", "title": "Closed", "status": ParsedVacancy.Status.CLOSED},
        )

        with pytest.raises(ApplicationError, match="Closed or expired"):
            import_parsed_vacancy(parsed_vacancy=parsed, created_by=hr_user)


class TestTelegramParser:
    def test_parse_telegram_job_message_creates_active_vacancy(self, company, hr_user):
        source = _source(company, hr_user, ParsedVacancySource.Type.TELEGRAM)
        parsed = parse_telegram_job_message(
            source=source,
            message_text="Backend Developer\nSalary: 1000-2000 USD\nLocation: Tashkent\nContact: @hr_user\n#Python #Django",
            message_id="123",
            message_url="https://t.me/jobs/123",
        )

        assert parsed.title == "Backend Developer"
        assert parsed.status == ParsedVacancy.Status.ACTIVE
        assert parsed.salary_min == 1000
        assert parsed.salary_max == 2000
        assert parsed.location == "Tashkent"
        assert parsed.skills == ["Python", "Django"]

    def test_parse_telegram_job_message_rejects_missing_contact(self, company, hr_user):
        source = _source(company, hr_user, ParsedVacancySource.Type.TELEGRAM)

        with pytest.raises(ApplicationError, match="contact information"):
            parse_telegram_job_message(
                source=source,
                message_text="Backend Developer\nSalary: 1000-2000 USD\nLocation: Tashkent",
                message_id="no-contact",
            )

        assert ParsedVacancy.objects.filter(source=source).count() == 0

    def test_refresh_telegram_actuality_marks_old_posts_stale(self, company, hr_user):
        source = _source(company, hr_user, ParsedVacancySource.Type.TELEGRAM)
        source.settings = {"ttl_days": 7}
        source.save(update_fields=["settings", "updated_at"])
        parsed = upsert_parsed_vacancy(source=source, payload={"external_id": "old", "title": "Old Telegram role"})
        parsed.last_seen_at = timezone.now() - timedelta(days=8)
        parsed.save(update_fields=["last_seen_at", "updated_at"])

        assert refresh_telegram_actuality() == 1
        parsed.refresh_from_db()
        assert parsed.status == ParsedVacancy.Status.STALE


class TestHeadHunterSync:
    def test_sync_hh_source_upserts_items_and_marks_missing_as_stale(self, company, hr_user):
        source = _source(company, hr_user)
        ParsedVacancy.objects.create(
            source=source,
            external_id="old",
            title="Old role",
            status=ParsedVacancy.Status.ACTIVE,
            last_seen_at=timezone.now() - timedelta(days=2),
            fingerprint="old",
        )
        list_response = Mock()
        list_response.json.return_value = {
            "items": [
                {
                    "id": "new",
                    "name": "Python Engineer",
                    "alternate_url": "https://hh.ru/vacancy/new",
                    "employer": {"name": "Acme"},
                    "area": {"name": "Tashkent"},
                    "salary": {"from": 1500, "to": 2500, "currency": "USD"},
                    "snippet": {"responsibility": "Build APIs", "requirement": "Python"},
                    "published_at": "2026-04-20T10:00:00+0300",
                }
            ]
        }
        list_response.raise_for_status.return_value = None
        detail_response = Mock()
        detail_response.json.return_value = {
            "id": "new",
            "contacts": {"email": "hr@example.com", "phones": []},
            "key_skills": [{"name": "Python"}],
        }
        detail_response.raise_for_status.return_value = None

        with patch("apps.job_parser.services.hh.requests.get", side_effect=[list_response, detail_response]):
            result = sync_hh_source(source=source)

        parsed = ParsedVacancy.objects.get(source=source, external_id="new")
        assert result["parsed"] == 1
        assert result["skipped_no_contact"] == 0
        assert parsed.title == "Python Engineer"
        assert parsed.salary_min == 1500
        assert ParsedVacancy.objects.get(source=source, external_id="old").status == ParsedVacancy.Status.STALE

    def test_sync_hh_source_skips_items_without_contact(self, company, hr_user):
        source = _source(company, hr_user)
        list_response = Mock()
        list_response.json.return_value = {
            "items": [
                {
                    "id": "no-contact",
                    "name": "Hidden Recruiter Role",
                    "alternate_url": "https://hh.ru/vacancy/no-contact",
                    "snippet": {"responsibility": "Build APIs"},
                }
            ]
        }
        list_response.raise_for_status.return_value = None
        detail_response = Mock()
        detail_response.json.return_value = {"id": "no-contact", "contacts": None, "description": "No contacts here"}
        detail_response.raise_for_status.return_value = None

        with patch("apps.job_parser.services.hh.requests.get", side_effect=[list_response, detail_response]):
            result = sync_hh_source(source=source)

        assert result["parsed"] == 0
        assert result["skipped_no_contact"] == 1
        assert ParsedVacancy.objects.filter(source=source, external_id="no-contact").exists() is False

    def test_sync_hh_source_does_not_require_url_or_filters(self, company, hr_user):
        source = ParsedVacancySource.objects.create(
            company=company,
            created_by=hr_user,
            name="All HH vacancies",
            source_type=ParsedVacancySource.Type.HH_UZ,
            is_active=True,
        )
        list_response = Mock()
        list_response.json.return_value = {"items": [], "pages": 1}
        list_response.raise_for_status.return_value = None

        with patch("apps.job_parser.services.hh.requests.get", return_value=list_response) as request_get:
            result = sync_hh_source(source=source)

        assert result["parsed"] == 0
        request_get.assert_called_once()
        assert request_get.call_args.kwargs["params"] == {"per_page": 100, "page": 0}


class TestParserSyncControl:
    def test_start_source_sync_queues_celery_task(self, company, hr_user):
        source = _source(company, hr_user)

        with patch("apps.job_parser.tasks.sync_parsed_vacancy_source_task.apply_async") as apply_async:
            updated = start_source_sync(source=source)

        assert updated.sync_status == ParsedVacancySource.SyncStatus.RUNNING
        assert updated.sync_task_id
        apply_async.assert_called_once_with(args=[str(source.id)], task_id=updated.sync_task_id)

    def test_start_source_sync_rejects_telegram_source(self, company, hr_user):
        source = _source(company, hr_user, ParsedVacancySource.Type.TELEGRAM)

        with pytest.raises(ApplicationError, match="Only HeadHunter"):
            start_source_sync(source=source)

    def test_start_source_sync_rejects_disabled_source(self, company, hr_user):
        source = _source(company, hr_user, is_active=False)

        with pytest.raises(ApplicationError, match="disabled"):
            start_source_sync(source=source)

    def test_stop_source_sync_revokes_celery_task(self, company, hr_user):
        source = _source(company, hr_user)
        source.sync_status = ParsedVacancySource.SyncStatus.RUNNING
        source.sync_task_id = "task-123"
        source.save(update_fields=["sync_status", "sync_task_id", "updated_at"])

        with patch("apps.job_parser.tasks.sync_parsed_vacancy_source_task.app.control.revoke") as revoke:
            updated = stop_source_sync(source=source)

        assert updated.sync_status == ParsedVacancySource.SyncStatus.CANCELLED
        assert updated.sync_finished_at is not None
        revoke.assert_called_once_with("task-123")
