import io
import logging
import uuid
from uuid import UUID

import boto3
from botocore.config import Config as BotoConfig
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from openai import OpenAI

from apps.accounts.models import User
from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
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
        Application.Status.INTERVIEW_IN_PROGRESS,
        Application.Status.REVIEWING,
        Application.Status.REJECTED,
        Application.Status.EXPIRED,
    },
    Application.Status.INTERVIEW_IN_PROGRESS: {
        Application.Status.INTERVIEW_COMPLETED,
        Application.Status.APPLIED,
        Application.Status.REJECTED,
    },
    Application.Status.INTERVIEW_COMPLETED: {
        Application.Status.APPLIED,
        Application.Status.REVIEWING,
        Application.Status.SHORTLISTED,
        Application.Status.REJECTED,
    },
    Application.Status.REVIEWING: {
        Application.Status.APPLIED,
        Application.Status.SHORTLISTED,
        Application.Status.REJECTED,
    },
    Application.Status.SHORTLISTED: {
        Application.Status.APPLIED,
        Application.Status.REJECTED,
    },
    Application.Status.REJECTED: {
        Application.Status.APPLIED,
    },
    Application.Status.EXPIRED: {
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

    Creates both the Application and a PENDING Interview record immediately.
    Returns a dict with the application and interview info (including token).
    """
    try:
        vacancy = Vacancy.objects.get(id=vacancy_id)
    except Vacancy.DoesNotExist:
        raise ApplicationError("Vacancy not found.")

    if vacancy.status != Vacancy.Status.PUBLISHED:
        raise ApplicationError("This vacancy is not accepting applications.")

    if vacancy.cv_required and not cv_file_path:
        raise ApplicationError("A CV is required for this vacancy.")

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
        raise ApplicationError("You have already applied to this vacancy.")

    if cv_file_path:
        from django.db import transaction
        from apps.applications.tasks import process_cv

        transaction.on_commit(lambda: process_cv.delay(str(application.id)))

    # Create Interview record immediately (AI is always available)
    interview_kwargs: dict = {
        "application": application,
        "screening_mode": vacancy.screening_mode,
        "status": Interview.Status.PENDING,
    }
    if vacancy.screening_mode == Interview.ScreeningMode.MEET:
        interview_kwargs["duration_minutes"] = vacancy.interview_duration
        interview_kwargs["livekit_room_name"] = f"interview-{application.id}"

    interview = Interview.objects.create(**interview_kwargs)

    return {
        "application": application,
        "interview": interview,
        "interview_token": str(interview.interview_token),
    }


def update_application_status(
    *,
    application: Application,
    status: str,
    updated_by: User,
) -> Application:
    """Update the status of an application with transition validation."""
    current = application.status
    allowed = _STATUS_TRANSITIONS.get(current, set())

    if status not in allowed:
        raise ApplicationError(
            f"Cannot transition from '{current}' to '{status}'."
        )

    application.status = status
    application.save(update_fields=["status", "updated_at"])
    return application


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
    """Extract text from PDF bytes using PyPDF2."""
    import PyPDF2

    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
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
    """AI analysis of CV to extract structured data using OpenAI."""
    import json as _json

    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        logger.error("analyze_cv_with_ai: application %s not found", application_id)
        return

    if not application.cv_parsed_text:
        logger.warning("analyze_cv_with_ai: no cv_parsed_text for %s, skipping", application_id)
        return

    logger.info("analyze_cv_with_ai: calling OpenAI for application %s", application_id)
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
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
            },
            {
                "role": "user",
                "content": f"Parse this CV:\n\n{application.cv_parsed_text[:8000]}",
            },
        ],
    )

    parsed = _json.loads(response.choices[0].message.content)
    application.cv_parsed_data = parsed
    application.save(update_fields=["cv_parsed_data", "updated_at"])
    logger.info("analyze_cv_with_ai: saved parsed data for application %s", application_id)


def calculate_match_score(*, application_id: UUID) -> None:
    """Compare CV against vacancy requirements and compute match score using OpenAI."""
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

    logger.info("calculate_match_score: calling OpenAI for application %s", application_id)
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an HR matching expert. Compare a candidate's CV against a job vacancy "
                    "and provide a match score. Return JSON with:\n"
                    '- "overall": number 0-100 (overall match percentage)\n'
                    '- "criteria_scores": {technical_skills: 0-100, experience_relevance: 0-100, education_fit: 0-100}\n'
                    '- "notes": brief explanation of the match assessment\n'
                    '- "matching_skills": list of skills that match the vacancy\n'
                    '- "missing_skills": list of required skills the candidate lacks'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"VACANCY: {vacancy.title}\n"
                    f"Requirements: {vacancy.requirements or 'N/A'}\n"
                    f"Skills needed: {', '.join(vacancy.skills) if vacancy.skills else 'N/A'}\n"
                    f"Experience level: {vacancy.experience_level}\n\n"
                    f"CANDIDATE CV SUMMARY:\n{cv_text[:4000]}"
                ),
            },
        ],
    )

    match_data = _json.loads(response.choices[0].message.content)
    application.match_score = round(float(match_data.get("overall", 0)), 2)
    application.match_details = match_data
    application.save(
        update_fields=["match_score", "match_details", "updated_at"]
    )
    logger.info("calculate_match_score: score=%.1f for application %s", application.match_score, application_id)


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

        # Trigger notification
        from apps.notifications.services import notify_status_changed

        notify_status_changed(application=application)
        updated += 1

    return updated


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
