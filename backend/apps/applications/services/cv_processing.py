import io
import logging
from uuid import UUID

from django.conf import settings
from google import genai
from google.genai import types

from apps.applications.models import Application
from apps.applications.services.s3_utils import _get_s3_client

logger = logging.getLogger(__name__)


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

    if not text.strip() and application.cv_parsed_text:
        logger.warning("process_cv_text: extracted no text for %s, keeping existing profile snapshot", application_id)
        return

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
                parts=[types.Part(text=f"Parse this CV:\n\n{application.cv_parsed_text[:8000]}")],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=(
                "You are a CV/resume parser. Extract structured data from the CV text. "
                "Write the summary and all descriptions in the SAME language as the CV content. "
                "If the CV is in Russian, output in Russian. If in English, output in English. If in Uzbek, output in Uzbek. "
                "Return JSON with these fields:\n"
                '- "contacts": {email, phone, location, linkedin, github, website, telegram} (strings, null if not found)\n'
                '- "skills": list of technical and soft skills\n'
                '- "experience_years": estimated total years of professional experience (number)\n'
                '- "experience": list of {company, role, duration, description}\n'
                '- "education": list of {degree, field, institution, year}\n'
                '- "languages": list of {language, level} (e.g. English - Fluent)\n'
                '- "certifications": list of strings (certifications, courses)\n'
                '- "summary": 2-3 sentence professional summary\n'
                '- "content_language": detected language code of the CV (en, ru, or uz)\n'
                "If any field cannot be determined, use empty list, empty object, or null."
            ),
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    parsed = _json.loads(response.text)
    application.cv_parsed_data = parsed
    detected_lang = parsed.get("content_language", "en")
    summary = parsed.get("summary", "")
    application.cv_summary_translations = {detected_lang: summary} if summary else {}
    application.save(update_fields=["cv_parsed_data", "cv_summary_translations", "updated_at"])
    logger.info("analyze_cv_with_ai: saved parsed data for application %s", application_id)


def calculate_match_score(*, application_id: UUID) -> None:
    """Compare CV against vacancy requirements and compute match score using Gemini."""
    import json as _json

    try:
        application = Application.objects.select_related("vacancy").get(id=application_id)
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
                parts=[
                    types.Part(
                        text=f"VACANCY: {vacancy.title}\n"
                        f"Requirements: {vacancy.requirements or 'N/A'}\n"
                        f"Skills needed: {', '.join(vacancy.skills) if vacancy.skills else 'N/A'}\n"
                        f"Experience level: {vacancy.experience_level}\n\n"
                        f"CANDIDATE CV SUMMARY:\n{cv_text[:4000]}"
                    )
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction=(
                "You are an HR matching expert. Compare a candidate's CV against a job vacancy "
                "and provide a match score. "
                "Write the notes in the same language as the CV content. "
                "Return JSON with:\n"
                '- "overall": number 0-100 (overall match percentage)\n'
                '- "criteria_scores": {technical_skills: 0-100, experience_relevance: 0-100, education_fit: 0-100}\n'
                '- "notes": brief explanation of the match assessment\n'
                '- "matching_skills": list of skills that match the vacancy\n'
                '- "missing_skills": list of required skills the candidate lacks\n'
                '- "content_language": detected language code of the CV (en, ru, or uz)'
            ),
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    match_data = _json.loads(response.text)
    application.match_score = round(float(match_data.get("overall", 0)), 2)
    application.match_details = match_data
    detected_lang = match_data.get("content_language", "en")
    notes = match_data.get("notes", "")
    application.match_notes_translations = {detected_lang: notes} if notes else {}
    application.save(update_fields=["match_score", "match_details", "match_notes_translations", "updated_at"])
    logger.info("calculate_match_score: score=%.1f for application %s", application.match_score, application_id)
