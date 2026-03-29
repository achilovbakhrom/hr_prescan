from decimal import Decimal

import pytest

from apps.applications.models import Application
from apps.applications.services import (
    bulk_move_by_filter,
    create_interview_session,
    soft_delete_applications,
    submit_application,
    update_application_status,
)
from apps.common.exceptions import ApplicationError
from apps.interviews.models import Interview
from tests.factories import ApplicationFactory, InterviewFactory


class TestSubmitApplication:
    def test_submit_application_creates_prescanning_session(self, vacancy):
        """Submitting an application creates both the Application and a prescanning session."""
        result = submit_application(
            vacancy_id=vacancy.id,
            candidate_name="Jane Doe",
            candidate_email="jane@example.com",
        )

        app = result["application"]
        assert app.candidate_name == "Jane Doe"
        assert app.candidate_email == "jane@example.com"
        assert app.status == Application.Status.APPLIED
        assert app.vacancy == vacancy

        # A prescanning session should have been created
        session = app.sessions.first()
        assert session is not None
        assert session.session_type == Interview.SessionType.PRESCANNING
        assert session.screening_mode == Interview.ScreeningMode.CHAT
        assert session.status == Interview.Status.PENDING

        # The returned token should match
        assert result["prescan_token"] == str(session.interview_token)

    def test_submit_application_duplicate_email_fails(self, vacancy):
        """Submitting the same email to the same vacancy raises an error."""
        submit_application(
            vacancy_id=vacancy.id,
            candidate_name="Jane Doe",
            candidate_email="jane@example.com",
        )

        with pytest.raises(ApplicationError, match="already applied"):
            submit_application(
                vacancy_id=vacancy.id,
                candidate_name="Jane Doe Again",
                candidate_email="jane@example.com",
            )


class TestStatusTransitions:
    def test_status_transitions_valid(self, vacancy, hr_user):
        """A valid transition (applied -> prescanned) should succeed."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)

        updated = update_application_status(
            application=app,
            status=Application.Status.PRESCANNED,
            updated_by=hr_user,
        )

        assert updated.status == Application.Status.PRESCANNED

    def test_status_transitions_invalid(self, vacancy, hr_user):
        """An invalid transition (applied -> interviewed) should raise an error."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)

        with pytest.raises(ApplicationError, match="Cannot transition"):
            update_application_status(
                application=app,
                status=Application.Status.INTERVIEWED,
                updated_by=hr_user,
            )

    def test_reset_to_applied_cancels_sessions(self, vacancy, hr_user):
        """Moving back to 'applied' cancels active sessions and creates a new prescanning session."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)
        old_session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.PENDING,
        )

        update_application_status(
            application=app,
            status=Application.Status.APPLIED,
            updated_by=hr_user,
        )

        old_session.refresh_from_db()
        assert old_session.status == Interview.Status.CANCELLED

        # A new prescanning session should exist
        new_session = app.sessions.filter(
            status=Interview.Status.PENDING,
            session_type=Interview.SessionType.PRESCANNING,
        ).latest("created_at")
        assert new_session is not None
        assert new_session.id != old_session.id


class TestCreateInterviewSession:
    def test_create_interview_session_when_enabled(self, vacancy):
        """Creates an interview session if vacancy.interview_enabled is True."""
        vacancy.interview_enabled = True
        vacancy.save(update_fields=["interview_enabled"])

        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)

        session = create_interview_session(application=app)

        assert session is not None
        assert session.session_type == Interview.SessionType.INTERVIEW
        assert session.screening_mode == vacancy.interview_mode
        assert session.status == Interview.Status.PENDING

    def test_create_interview_session_when_disabled(self, vacancy):
        """Returns None if vacancy.interview_enabled is False."""
        vacancy.interview_enabled = False
        vacancy.save(update_fields=["interview_enabled"])

        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)

        session = create_interview_session(application=app)

        assert session is None


class TestSoftDelete:
    def test_soft_delete_only_archived(self, vacancy, hr_user):
        """Soft delete only works on applications with 'archived' status."""
        archived_app = ApplicationFactory(
            vacancy=vacancy, status=Application.Status.ARCHIVED
        )
        applied_app = ApplicationFactory(
            vacancy=vacancy, status=Application.Status.APPLIED
        )

        count = soft_delete_applications(
            application_ids=[archived_app.id, applied_app.id],
            updated_by=hr_user,
        )

        assert count == 1

        archived_app.refresh_from_db()
        assert archived_app.is_deleted is True

        applied_app.refresh_from_db()
        assert applied_app.is_deleted is False


class TestBulkMoveByFilter:
    def test_bulk_move_by_filter_score(self, vacancy, hr_user):
        """Batch move with score threshold filters correctly."""
        app_low = ApplicationFactory(
            vacancy=vacancy,
            status=Application.Status.APPLIED,
            match_score=Decimal("20.00"),
        )
        app_high = ApplicationFactory(
            vacancy=vacancy,
            status=Application.Status.APPLIED,
            match_score=Decimal("80.00"),
        )

        count = bulk_move_by_filter(
            vacancy_id=vacancy.id,
            from_status=Application.Status.APPLIED,
            to_status=Application.Status.REJECTED,
            updated_by=hr_user,
            max_score=50.0,
        )

        assert count == 1

        app_low.refresh_from_db()
        assert app_low.status == Application.Status.REJECTED

        app_high.refresh_from_db()
        assert app_high.status == Application.Status.APPLIED
