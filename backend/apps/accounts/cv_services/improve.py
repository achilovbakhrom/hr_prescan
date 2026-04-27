from django.conf import settings

SECTION_LABELS = {
    "headline": "headline",
    "summary": "professional summary",
    "experience_description": "work experience description",
}


def improve_cv_section(*, section, content, job_title=None):
    """Use AI to improve a CV section text."""
    from google import genai

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    context = f" tailored for a {job_title} position" if job_title else ""
    section_label = SECTION_LABELS.get(section, section)
    prompt = f"""Improve this {section_label} text for a professional CV{context}.
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
