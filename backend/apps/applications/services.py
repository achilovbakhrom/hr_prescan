import io
import logging
import uuid
from uuid import UUID

import boto3
from botocore.config import Config as BotoConfig
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from google import genai
from google.genai import types

from apps.accounts.models import User
from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_ALREADY_APPLIED,
    MSG_CV_REQUIRED,
    MSG_STATUS_TRANSITION_INVALID,
    MSG_VACANCY_NOT_ACCEPTING,
    MSG_VACANCY_NOT_FOUND,
)
from apps.interviews.models import Interview
from apps.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=BotoConfig(signature_version="s3v4"),
    )


def upload_cv_to_s3(*, file_obj, vacancy_id) -> str:
    """Upload a CV file to S3/MinIO and return the object key."""
    ext = file_obj.name.rsplit(".", 1)[-1] if "." in file_obj.name else "pdf"
    key = f"cvs/{vacancy_id}/{uuid.uuid4()}.{ext}"

    s3 = _get_s3_client()
    s3.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": file_obj.content_type or "application/octet-stream"},
    )
    return key


def generate_cv_download_url(*, cv_file_path: str, expiration: int = 3600) -> str:
    """Generate a presigned URL for downloading a CV from S3/MinIO."""
    s3 = _get_s3_client()
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": cv_file_path,
        },
        ExpiresIn=expiration,
    )


# Valid status transitions: current_status -> set of allowed next statuses
_STATUS_TRANSITIONS: dict[str, set[str]] = {
    Application.Status.APPLIED: {
        Application.Status.PRESCANNED,
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.EXPIRED,
    },
    Application.Status.PRESCANNED: {
        Application.Status.INTERVIEWED,
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.APPLIED,
        Application.Status.EXPIRED,
    },
    Application.Status.INTERVIEWED: {
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.PRESCANNED,
    },
    Application.Status.SHORTLISTED: {
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.APPLIED,
    },
    Application.Status.HIRED: {
        Application.Status.ARCHIVED,
    },
    Application.Status.REJECTED: {
        Application.Status.APPLIED,
        Application.Status.ARCHIVED,
    },
    Application.Status.EXPIRED: {
        Application.Status.APPLIED,
        Application.Status.ARCHIVED,
    },
    Application.Status.ARCHIVED: {
        Application.Status.APPLIED,
    },
}


def submit_application(
    *,
    vacancy_id: UUID,
    candidate_name: str,
    candidate_email: str,
    candidate_phone: str = "",
    cv_file_path: str = "",
    cv_original_filename: str = "",
    candidate: User | None = None,
) -> dict:
    """Submit a new application to a vacancy.

    Creates the Application and a PENDING prescanning session immediately.
    Returns a dict with the application and prescanning session info.
    """
    try:
        vacancy = Vacancy.objects.get(id=vacancy_id)
    except Vacancy.DoesNotExist:
        raise ApplicationError(str(MSG_VACANCY_NOT_FOUND))

    if vacancy.status != Vacancy.Status.PUBLISHED:
        raise ApplicationError(str(MSG_VACANCY_NOT_ACCEPTING))

    if vacancy.cv_required and not cv_file_path:
        raise ApplicationError(str(MSG_CV_REQUIRED))

    try:
        application = Application.objects.create(
            vacancy=vacancy,
            candidate=candidate,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            cv_file=cv_file_path,
            cv_original_filename=cv_original_filename,
        )
    except IntegrityError:
        raise ApplicationError(str(MSG_ALREADY_APPLIED))

    if cv_file_path:
        from django.db import transaction
        from apps.applications.tasks import process_cv

        transaction.on_commit(lambda: process_cv.delay(str(application.id)))

    # Create prescanning session immediately (always chat mode)
    prescan_session = Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.PENDING,
    )

    return {
        "application": application,
        "prescan_session": prescan_session,
        "prescan_token": str(prescan_session.interview_token),
    }


def create_interview_session(*, application: Application) -> Interview | None:
    """Create an interview session for a prescanned application.

    Only creates if the vacancy has interview_enabled=True.
    Returns the new Interview session or None if interview not enabled.
    """
    vacancy = application.vacancy
    if not vacancy.interview_enabled:
        return None

    interview_kwargs: dict = {
        "application": application,
        "session_type": Interview.SessionType.INTERVIEW,
        "screening_mode": vacancy.interview_mode,
        "status": Interview.Status.PENDING,
    }
    if vacancy.interview_mode == Interview.ScreeningMode.MEET:
        interview_kwargs["duration_minutes"] = vacancy.interview_duration
        interview_kwargs["livekit_room_name"] = f"interview-{application.id}"

    return Interview.objects.create(**interview_kwargs)


def update_application_status(
    *,
    application: Application,
    status: str,
    updated_by: User,
) -> Application:
    """Update the status of an application with transition validation.

    When resetting to Applied, cancels all existing sessions and creates
    a fresh prescanning session (full pipeline restart).
    """
    current = application.status
    allowed = _STATUS_TRANSITIONS.get(current, set())

    if status not in allowed:
        raise ApplicationError(
            str(MSG_STATUS_TRANSITION_INVALID).format(current=current, target=status)
        )

    # Reset to Applied = full pipeline restart
    if status == Application.Status.APPLIED and current != Application.Status.APPLIED:
        _reset_pipeline(application=application)

    application.status = status
    application.save(update_fields=["status", "updated_at"])
    return application


def _reset_pipeline(*, application: Application) -> None:
    """Cancel all existing sessions and create a fresh prescanning session."""
    # Cancel all non-completed, non-cancelled sessions
    active_sessions = application.sessions.exclude(
        status__in=[Interview.Status.COMPLETED, Interview.Status.CANCELLED, Interview.Status.EXPIRED]
    )
    active_sessions.update(status=Interview.Status.CANCELLED)

    # Create fresh prescanning session
    Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.PENDING,
    )


def add_hr_note(*, application: Application, note: str) -> Application:
    """Append a note to the application's HR notes."""
    if application.hr_notes:
        application.hr_notes += f"\n\n---\n\n{note}"
    else:
        application.hr_notes = note

    application.save(update_fields=["hr_notes", "updated_at"])
    return application


def process_cv_text(*, application_id: UUID) -> None:
    """Extract text from CV file stored in S3/MinIO."""
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        logger.error("process_cv_text: application %s not found", application_id)
        return

    if not application.cv_file:
        logger.warning("process_cv_text: no cv_file for application %s", application_id)
        return

    logger.info("process_cv_text: downloading %s for application %s", application.cv_file, application_id)
    s3 = _get_s3_client()
    response = s3.get_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=application.cv_file,
    )
    file_bytes = response["Body"].read()
    logger.info("process_cv_text: downloaded %d bytes", len(file_bytes))

    ext = application.cv_file.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        text = _extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        text = _extract_text_from_docx(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    application.cv_parsed_text = text[:50000]
    application.save(update_fields=["cv_parsed_text", "updated_at"])
    logger.info("process_cv_text: saved %d chars for application %s", len(text), application_id)


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pypdf."""
    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    import docx

    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def analyze_cv_with_ai(*, application_id: UUID) -> None:
    """AI analysis of CV to extract structured data using Gemini."""
    import json as _json

    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        logger.error("analyze_cv_with_ai: application %s not found", application_id)
        return

    if not application.cv_parsed_text:
        logger.warning("analyze_cv_with_ai: no cv_parsed_text for %s, skipping", application_id)
        return

    logger.info("analyze_cv_with_ai: calling Gemini for application %s", application_id)
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=
                    f"Parse this CV:\n\n{application.cv_parsed_text[:8000]}"
                )],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=(
                "You are a CV/resume parser. Extract structured data from the CV text. "
                "Return JSON with these fields:\n"
                '- "contacts": {email, phone, location, linkedin, github, website, telegram} (strings, null if not found)\n'
                '- "skills": list of technical and soft skills\n'
                '- "experience_years": estimated total years of professional experience (number)\n'
                '- "experience": list of {company, role, duration, description}\n'
                '- "education": list of {degree, field, institution, year}\n'
                '- "languages": list of {language, level} (e.g. English - Fluent)\n'
                '- "certifications": list of strings (certifications, courses)\n'
                '- "summary": 2-3 sentence professional summary\n'
                "If any field cannot be determined, use empty list, empty object, or null."
            ),
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    parsed = _json.loads(response.text)
    application.cv_parsed_data = parsed
    application.save(update_fields=["cv_parsed_data", "updated_at"])
    logger.info("analyze_cv_with_ai: saved parsed data for application %s", application_id)


def calculate_match_score(*, application_id: UUID) -> None:
    """Compare CV against vacancy requirements and compute match score using Gemini."""
    import json as _json

    try:
        application = Application.objects.select_related("vacancy").get(
            id=application_id
        )
    except Application.DoesNotExist:
        logger.error("calculate_match_score: application %s not found", application_id)
        return

    vacancy = application.vacancy
    cv_text = application.cv_parsed_text or ""

    if not cv_text:
        logger.warning("calculate_match_score: no cv_text for %s, skipping", application_id)
        return

    logger.info("calculate_match_score: calling Gemini for application %s", application_id)
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=
                    f"VACANCY: {vacancy.title}\n"
                    f"Requirements: {vacancy.requirements or 'N/A'}\n"
                    f"Skills needed: {', '.join(vacancy.skills) if vacancy.skills else 'N/A'}\n"
                    f"Experience level: {vacancy.experience_level}\n\n"
                    f"CANDIDATE CV SUMMARY:\n{cv_text[:4000]}"
                )],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=(
                "You are an HR matching expert. Compare a candidate's CV against a job vacancy "
                "and provide a match score. Return JSON with:\n"
                '- "overall": number 0-100 (overall match percentage)\n'
                '- "criteria_scores": {technical_skills: 0-100, experience_relevance: 0-100, education_fit: 0-100}\n'
                '- "notes": brief explanation of the match assessment\n'
                '- "matching_skills": list of skills that match the vacancy\n'
                '- "missing_skills": list of required skills the candidate lacks'
            ),
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    match_data = _json.loads(response.text)
    application.match_score = round(float(match_data.get("overall", 0)), 2)
    application.match_details = match_data
    application.save(
        update_fields=["match_score", "match_details", "updated_at"]
    )
    logger.info("calculate_match_score: score=%.1f for application %s", application.match_score, application_id)


@transaction.atomic
def bulk_update_status(
    *,
    application_ids: list[UUID],
    status: str,
    updated_by: User,
) -> int:
    """Update multiple applications to a new status. Returns count of updated records.

    Only transitions that are valid per _STATUS_TRANSITIONS are applied;
    applications that cannot transition are silently skipped.
    """
    from apps.notifications.services import notify_status_changed

    applications = Application.objects.filter(
        id__in=application_ids,
        vacancy__company=updated_by.company,
    ).select_related("vacancy")

    updated = 0
    for application in applications:
        allowed = _STATUS_TRANSITIONS.get(application.status, set())
        if status not in allowed:
            continue

        application.status = status
        application.save(update_fields=["status", "updated_at"])

        notify_status_changed(application=application)
        updated += 1

    return updated


def soft_delete_applications(
    *,
    application_ids: list[UUID],
    updated_by: User,
) -> int:
    """Soft-delete applications (clear from archive). Completely hidden from UI."""
    from django.utils import timezone

    return Application.objects.filter(
        id__in=application_ids,
        vacancy__company=updated_by.company,
        status=Application.Status.ARCHIVED,
    ).update(is_deleted=True, updated_at=timezone.now())


def bulk_move_by_filter(
    *,
    vacancy_id: UUID,
    from_status: str,
    to_status: str,
    updated_by: User,
    max_score: float | None = None,
    min_score: float | None = None,
    score_field: str = "match_score",
    has_cv: bool | None = None,
    days_since_applied: int | None = None,
) -> int:
    """Batch move candidates from one status to another with optional filters.

    Args:
        from_status: Source status to filter candidates.
        to_status: Target status to move to.
        max_score: Only include candidates with score < this value.
        min_score: Only include candidates with score > this value.
        score_field: Which score to filter by: match_score, prescanning_score, interview_score.
        has_cv: Filter by whether candidate has a CV.
        days_since_applied: Only include candidates applied more than X days ago.
    """
    from django.utils import timezone as tz
    from datetime import timedelta

    # Validate transition
    allowed = _STATUS_TRANSITIONS.get(from_status, set())
    if to_status not in allowed:
        raise ApplicationError(
            str(MSG_STATUS_TRANSITION_INVALID).format(current=from_status, target=to_status)
        )

    qs = Application.objects.filter(
        vacancy_id=vacancy_id,
        vacancy__company=updated_by.company,
        status=from_status,
        is_deleted=False,
    )

    # Score filters — for prescanning/interview scores, join through sessions
    if score_field == "match_score":
        if max_score is not None:
            qs = qs.filter(match_score__lt=max_score)
        if min_score is not None:
            qs = qs.filter(match_score__gt=min_score)
    elif score_field in ("prescanning_score", "interview_score"):
        session_type = "prescanning" if score_field == "prescanning_score" else "interview"
        session_filter = Q(
            sessions__session_type=session_type,
            sessions__status="completed",
        )
        if max_score is not None:
            session_filter &= Q(sessions__overall_score__lt=max_score)
        if min_score is not None:
            session_filter &= Q(sessions__overall_score__gt=min_score)
        qs = qs.filter(session_filter).distinct()

    if has_cv is True:
        qs = qs.exclude(cv_file="")
    elif has_cv is False:
        qs = qs.filter(cv_file="")

    if days_since_applied is not None:
        cutoff = tz.now() - timedelta(days=days_since_applied)
        qs = qs.filter(created_at__lt=cutoff)

    count = qs.update(status=to_status)
    return count


def bind_existing_applications(*, user: User) -> int:
    """Bind anonymous applications to a newly registered user.

    Finds Applications where candidate_email (case-insensitive) matches
    user.email OR candidate_phone matches user.phone (if user has a phone),
    and candidate is NULL. Sets candidate=user on matching records.

    Returns the number of applications bound.
    """
    filter_q = Q(candidate__isnull=True, candidate_email__iexact=user.email)
    if user.phone:
        filter_q |= Q(candidate__isnull=True, candidate_phone=user.phone)

    return Application.objects.filter(filter_q).update(candidate=user)
