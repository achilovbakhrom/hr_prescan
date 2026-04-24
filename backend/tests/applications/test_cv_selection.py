import pytest

from apps.accounts.models import CandidateCV, CandidateProfile
from apps.applications.services import submit_application
from apps.common.exceptions import ApplicationError


def _create_platform_cv(*, user, name: str, file: str) -> None:
    profile = CandidateProfile.objects.create(user=user)
    CandidateCV.objects.create(
        profile=profile,
        name=name,
        file=file,
        is_active=True,
    )


def test_submit_application_uses_candidate_platform_cv(
    vacancy,
    candidate_user,
    monkeypatch,
    django_capture_on_commit_callbacks,
):
    """Authenticated candidates reuse their active platform CV when no CV is uploaded."""
    _create_platform_cv(
        user=candidate_user,
        name="Platform CV",
        file="cv-generated/candidate/platform.pdf",
    )
    queued = []
    monkeypatch.setattr("apps.applications.tasks.process_cv.delay", queued.append)

    with django_capture_on_commit_callbacks(execute=True):
        result = submit_application(
            vacancy_id=vacancy.id,
            candidate=candidate_user,
            candidate_name="Jane Doe",
            candidate_email=candidate_user.email,
        )

    app = result["application"]
    assert app.cv_file == "cv-generated/candidate/platform.pdf"
    assert app.cv_original_filename == "Platform CV"
    assert queued == [str(app.id)]


def test_submit_application_required_cv_accepts_candidate_platform_cv(vacancy, candidate_user, monkeypatch):
    """A required-CV vacancy accepts the candidate's existing platform CV."""
    vacancy.cv_required = True
    vacancy.save(update_fields=["cv_required"])
    _create_platform_cv(
        user=candidate_user,
        name="Required CV",
        file="cv-generated/candidate/required.pdf",
    )
    monkeypatch.setattr("apps.applications.tasks.process_cv.delay", lambda application_id: None)

    result = submit_application(
        vacancy_id=vacancy.id,
        candidate=candidate_user,
        candidate_name="Jane Doe",
        candidate_email=candidate_user.email,
    )

    assert result["application"].cv_file == "cv-generated/candidate/required.pdf"


def test_submit_application_required_cv_without_upload_or_platform_cv_fails(vacancy, candidate_user):
    """A required-CV vacancy still blocks candidates with no uploaded or platform CV."""
    vacancy.cv_required = True
    vacancy.save(update_fields=["cv_required"])

    with pytest.raises(ApplicationError, match="CV"):
        submit_application(
            vacancy_id=vacancy.id,
            candidate=candidate_user,
            candidate_name="Jane Doe",
            candidate_email=candidate_user.email,
        )
