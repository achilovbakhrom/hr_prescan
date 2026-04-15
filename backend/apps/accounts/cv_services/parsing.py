import json
import logging

from django.conf import settings

from apps.accounts.cv_services.profile import (
    _populate_profile_from_parsed,
    get_or_create_candidate_profile,
)

logger = logging.getLogger(__name__)


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
