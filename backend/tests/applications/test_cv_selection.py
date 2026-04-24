from datetime import date

import pytest

from apps.accounts.models import CandidateCV, CandidateProfile, WorkExperience
from apps.applications.services import submit_application
from apps.common.exceptions import ApplicationError
from apps.common.models import Skill


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


def test_submit_application_uses_candidate_profile_resume_without_file(
    vacancy,
    candidate_user,
    monkeypatch,
    django_capture_on_commit_callbacks,
):
    profile = CandidateProfile.objects.create(
        user=candidate_user,
        headline="Senior Driver",
        summary="Experienced family driver.",
        location="Tashkent",
    )
    skill = Skill.objects.create(slug="defensive-driving", name="Defensive driving")
    profile.skills.add(skill)
    WorkExperience.objects.create(
        profile=profile,
        company_name="Family Office",
        position="Driver",
        start_date=date(2020, 1, 1),
        description="Daily executive and family transportation.",
    )
    queued = []
    monkeypatch.setattr("apps.applications.tasks.calculate_cv_match.delay", queued.append)

    with django_capture_on_commit_callbacks(execute=True):
        result = submit_application(
            vacancy_id=vacancy.id,
            candidate=candidate_user,
            candidate_name="Jane Doe",
            candidate_email=candidate_user.email,
        )

    app = result["application"]
    assert app.cv_file == ""
    assert app.cv_parsed_data["summary"] == "Experienced family driver."
    assert app.cv_parsed_data["skills"] == ["Defensive driving"]
    assert app.cv_parsed_data["experience"][0]["company"] == "Family Office"
    assert "Daily executive" in app.cv_parsed_text
    assert queued == [str(app.id)]
