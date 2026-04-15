import pytest

from apps.common.exceptions import ApplicationError
from apps.interviews.models import Interview
from apps.vacancies.models import InterviewQuestion, ScreeningStep, Vacancy
from apps.vacancies.services import (
    archive_vacancy,
    create_vacancy,
    pause_vacancy,
    publish_vacancy,
)
from tests.factories import ApplicationFactory, InterviewFactory, VacancyFactory


class TestCreateVacancy:
    def test_create_vacancy_with_default_criteria(self, company, hr_user):
        """Creating a vacancy produces 5 default prescanning criteria."""
        vac = create_vacancy(
            company=company,
            created_by=hr_user,
            title="Backend Developer",
            description="We need a backend developer.",
        )

        criteria = vac.criteria.filter(is_default=True, step=ScreeningStep.PRESCANNING)
        assert criteria.count() == 5

        names = set(criteria.values_list("name", flat=True))
        assert "Technical Skills" in names
        assert "Communication" in names
        assert "Problem Solving" in names
        assert "Cultural Fit" in names
        assert "Experience Relevance" in names


class TestPublishVacancy:
    def test_publish_requires_prescanning_questions(self, company, hr_user):
        """Cannot publish a vacancy without active prescanning questions."""
        vac = VacancyFactory(
            company=company,
            created_by=hr_user,
            status=Vacancy.Status.DRAFT,
        )

        with pytest.raises(ApplicationError, match="prescanning questions"):
            publish_vacancy(vacancy=vac)

    def test_publish_with_interview_requires_interview_questions(self, company, hr_user):
        """If interview_enabled, publishing also requires active interview questions."""
        vac = VacancyFactory(
            company=company,
            created_by=hr_user,
            status=Vacancy.Status.DRAFT,
            interview_enabled=True,
        )
        # Add a prescanning question (required)
        InterviewQuestion.objects.create(
            vacancy=vac,
            text="Why do you want this role?",
            step=ScreeningStep.PRESCANNING,
            is_active=True,
            order=1,
        )
        # No interview questions yet

        with pytest.raises(ApplicationError, match="interview questions"):
            publish_vacancy(vacancy=vac)


class TestVacancyLifecycle:
    def test_vacancy_lifecycle_forward_only(self, vacancy):
        """draft -> published -> archived works; archived -> draft fails.

        Note: the fixture provides a published vacancy, so we archive it
        and then verify going back to draft is not allowed.
        """
        # Already published via fixture; archive it
        archived = archive_vacancy(vacancy=vacancy)
        assert archived.status == Vacancy.Status.ARCHIVED

        # Cannot go back to draft
        with pytest.raises(ApplicationError):
            publish_vacancy(vacancy=archived)

    def test_pause_and_resume(self, vacancy):
        """published -> paused -> published works."""
        paused = pause_vacancy(vacancy=vacancy)
        assert paused.status == Vacancy.Status.PAUSED

        resumed = publish_vacancy(vacancy=paused)
        assert resumed.status == Vacancy.Status.PUBLISHED


class TestArchiveVacancy:
    def test_archive_expires_pending_sessions(self, vacancy):
        """Archiving a vacancy expires all pending interview sessions."""
        app = ApplicationFactory(vacancy=vacancy, status="applied")
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.PENDING,
        )

        archive_vacancy(vacancy=vacancy)

        session.refresh_from_db()
        assert session.status == Interview.Status.EXPIRED
