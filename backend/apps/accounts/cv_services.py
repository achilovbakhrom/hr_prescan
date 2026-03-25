import json
import logging
import uuid

from django.conf import settings
from django.template.loader import render_to_string

from apps.accounts.models import CandidateCV, CandidateProfile

logger = logging.getLogger(__name__)


def get_or_create_candidate_profile(*, user):
    """Get or create CandidateProfile for user."""
    profile, _ = CandidateProfile.objects.get_or_create(user=user)
    return profile


def calculate_profile_completeness(*, profile):
    """Return {score: 0-100, sections: {personal: bool, summary: bool, experience: bool, education: bool, skills: bool, languages: bool}}"""
    sections = {
        "personal": bool(profile.headline and profile.location),
        "summary": bool(profile.summary),
        "experience": profile.work_experiences.exists(),
        "education": profile.educations.exists(),
        "skills": profile.skills.exists(),
        "languages": profile.languages.exists(),
    }
    filled = sum(sections.values())
    total = len(sections)
    return {"score": round(filled / total * 100), "sections": sections}


def generate_cv_pdf(*, profile, template_name="classic", cv_name="My CV"):
    """Generate PDF from profile data using WeasyPrint, upload to MinIO, return CandidateCV."""
    from weasyprint import HTML

    from apps.applications.services import _get_s3_client, generate_cv_download_url

    # 1. Prefetch all related data
    profile = (
        CandidateProfile.objects
        .select_related("user")
        .prefetch_related(
            "skills",
            "work_experiences",
            "educations__education_level",
            "languages__language",
            "certifications",
        )
        .get(pk=profile.pk)
    )

    # 2. Render HTML
    html_string = render_to_string(
        f"cv/{template_name}.html",
        {"profile": profile, "user": profile.user},
    )

    # 3. Convert to PDF
    pdf_bytes = HTML(string=html_string).write_pdf()

    # 4. Upload to MinIO
    file_key = f"cv-generated/{profile.user_id}/{uuid.uuid4()}.pdf"
    s3 = _get_s3_client()
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_key,
        Body=pdf_bytes,
        ContentType="application/pdf",
    )

    # 5. Deactivate other CVs, create new active one
    CandidateCV.objects.filter(profile=profile, is_active=True).update(is_active=False)
    cv = CandidateCV.objects.create(
        profile=profile,
        name=cv_name,
        template=template_name,
        file=file_key,
        is_active=True,
    )

    # 6. Generate presigned download URL
    download_url = generate_cv_download_url(cv_file_path=file_key)

    return cv, download_url


def parse_cv_with_ai(*, user, file_bytes, filename):
    """Parse uploaded CV file with AI and populate candidate profile."""
    from google import genai
    from google.genai import types

    profile = get_or_create_candidate_profile(user=user)

    # 1. Determine MIME type
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    mime_map = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    mime_type = mime_map.get(ext, "application/octet-stream")

    # 2. Call Gemini to extract structured data
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    prompt = """Extract structured CV data from this document. Return a JSON object with these fields:
{
  "headline": "professional title/headline",
  "summary": "professional summary paragraph",
  "location": "city, country",
  "work_experiences": [
    {"company_name": "", "position": "", "employment_type": "full_time|part_time|contract|internship", "location": "", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD or null if current", "is_current": true/false, "description": ""}
  ],
  "educations": [
    {"institution": "", "degree": "", "field_of_study": "", "start_date": "YYYY-MM-DD or null", "end_date": "YYYY-MM-DD or null", "description": ""}
  ],
  "skills": ["skill1", "skill2"],
  "languages": [
    {"language": "English", "proficiency": "native|advanced|upper_intermediate|intermediate|elementary|beginner"}
  ],
  "certifications": [
    {"name": "", "issuing_organization": "", "issue_date": "YYYY-MM-DD or null"}
  ]
}
Return ONLY valid JSON, no markdown, no explanation."""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            prompt,
        ],
    )

    # 3. Parse response
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    parsed = json.loads(text)

    # 4. Populate profile
    _populate_profile_from_parsed(profile=profile, data=parsed)

    return profile


def _populate_profile_from_parsed(*, profile, data):
    """Map AI-parsed data to profile models."""
    from apps.accounts.models import (
        CandidateLanguage,
        Certification,
        Education,
        WorkExperience,
    )
    from apps.common.models import Language, Skill

    # Update basic fields
    update_fields = []
    for field in ("headline", "summary", "location"):
        if data.get(field):
            setattr(profile, field, data[field])
            update_fields.append(field)
    if update_fields:
        profile.save(update_fields=update_fields + ["updated_at"])

    # Work experiences
    for exp in data.get("work_experiences", []):
        try:
            from datetime import date

            WorkExperience.objects.create(
                profile=profile,
                company_name=exp.get("company_name", ""),
                position=exp.get("position", ""),
                employment_type=exp.get("employment_type", ""),
                location=exp.get("location", ""),
                start_date=exp.get("start_date") or date.today(),
                end_date=exp.get("end_date"),
                is_current=exp.get("is_current", False),
                description=exp.get("description", ""),
            )
        except Exception:
            logger.warning("Failed to create work experience from parsed CV", exc_info=True)

    # Educations
    for edu in data.get("educations", []):
        try:
            Education.objects.create(
                profile=profile,
                institution=edu.get("institution", ""),
                degree=edu.get("degree", ""),
                field_of_study=edu.get("field_of_study", ""),
                start_date=edu.get("start_date"),
                end_date=edu.get("end_date"),
                description=edu.get("description", ""),
            )
        except Exception:
            logger.warning("Failed to create education from parsed CV", exc_info=True)

    # Skills -- fuzzy match against DB
    skill_names = data.get("skills", [])
    if skill_names:
        from django.db.models import Q

        q = Q()
        for name in skill_names:
            q |= Q(name__iexact=name) | Q(slug__iexact=name.lower().replace(" ", "-"))
        matched = Skill.objects.filter(q)
        profile.skills.add(*matched)

    # Languages
    for lang in data.get("languages", []):
        try:
            lang_name = lang.get("language", "")
            lang_obj = Language.objects.filter(name__iexact=lang_name).first()
            if lang_obj:
                CandidateLanguage.objects.get_or_create(
                    profile=profile,
                    language=lang_obj,
                    defaults={"proficiency": lang.get("proficiency", "intermediate")},
                )
        except Exception:
            logger.warning("Failed to create language from parsed CV", exc_info=True)

    # Certifications
    for cert in data.get("certifications", []):
        try:
            Certification.objects.create(
                profile=profile,
                name=cert.get("name", ""),
                issuing_organization=cert.get("issuing_organization", ""),
                issue_date=cert.get("issue_date"),
            )
        except Exception:
            logger.warning("Failed to create certification from parsed CV", exc_info=True)


def improve_cv_section(*, section, content, job_title=None):
    """Use AI to improve a CV section text."""
    from google import genai

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    context = f" tailored for a {job_title} position" if job_title else ""
    prompt = f"""Improve this {section} text for a professional CV{context}.
Make it more impactful, concise, and professional. Use action verbs and quantify achievements where possible.
Keep the same language (if Russian, write in Russian; if English, write in English).
Return ONLY the improved text, no explanations.

Original text:
{content}"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[prompt],
    )

    return response.text.strip()
