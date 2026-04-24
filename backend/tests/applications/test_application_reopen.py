from decimal import Decimal

from apps.applications.models import Application
from apps.applications.services import submit_application
from apps.interviews.models import Interview
from tests.factories import ApplicationFactory, InterviewFactory


def test_submit_application_reopens_archived_application(vacancy, candidate_user):
    app = ApplicationFactory(
        vacancy=vacancy,
        candidate=candidate_user,
        candidate_name="Old Name",
        candidate_email="jane@example.com",
        candidate_phone="+100",
        status=Application.Status.ARCHIVED,
        match_score=Decimal("72.00"),
        hr_notes="Old note",
    )
    old_created_at = app.created_at
    old_session = InterviewFactory(application=app, status=Interview.Status.PENDING)

    result = submit_application(
        vacancy_id=vacancy.id,
        candidate_name="Jane New",
        candidate_email="jane@example.com",
        candidate_phone="+200",
    )

    reopened = result["application"]
    assert reopened.id == app.id
    assert reopened.candidate == candidate_user
    assert reopened.candidate_name == "Jane New"
    assert reopened.candidate_phone == "+200"
    assert reopened.status == Application.Status.APPLIED
    assert reopened.is_deleted is False
    assert reopened.match_score is None
    assert reopened.hr_notes == ""
    assert reopened.created_at > old_created_at

    old_session.refresh_from_db()
    assert old_session.status == Interview.Status.CANCELLED
    assert result["prescan_session"].id != old_session.id
    assert result["prescan_session"].status == Interview.Status.PENDING


def test_submit_application_reopens_soft_deleted_application(vacancy):
    app = ApplicationFactory(
        vacancy=vacancy,
        candidate_email="jane@example.com",
        status=Application.Status.ARCHIVED,
        is_deleted=True,
    )

    result = submit_application(
        vacancy_id=vacancy.id,
        candidate_name="Jane New",
        candidate_email="jane@example.com",
    )

    assert result["application"].id == app.id
    assert result["application"].status == Application.Status.APPLIED
    assert result["application"].is_deleted is False
