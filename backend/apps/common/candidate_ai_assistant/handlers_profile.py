import json
import logging

logger = logging.getLogger(__name__)


def _handle_improve_cv_section(*, user, params):
    from django.conf import settings
    from google import genai
    from google.genai import types

    section = params.get("section", "summary")
    content = params.get("content", "")
    job_title = params.get("job_title", "")

    if not content.strip():
        return {
            "success": False,
            "message": "Please provide the text you want me to improve.",
            "data": {},
            "action": "improve_cv_section",
        }

    section_label = "Professional Summary" if section == "summary" else "Experience Description"
    job_context = f" for a {job_title} role" if job_title else ""

    prompt = (
        f"Improve the following {section_label}{job_context}. "
        f"Make it more professional, impactful, and ATS-friendly. "
        f"Use strong action verbs and quantifiable achievements where possible. "
        f"Keep it concise — no longer than the original unless needed for clarity. "
        f"Return ONLY the improved text, nothing else.\n\n"
        f"Original text:\n{content}"
    )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        improved_text = response.text.strip()
    except Exception as e:
        logger.error("CV improvement error: %s", e)
        return {
            "success": False,
            "message": "Failed to improve the text. Please try again.",
            "data": {},
            "action": "improve_cv_section",
        }

    return {
        "success": True,
        "message": f"Here's an improved version of your {section_label.lower()}:",
        "data": {
            "section": section,
            "original": content,
            "improved": improved_text,
        },
        "action": "improve_cv_section",
    }


def _handle_suggest_skills(*, user, params):
    from django.conf import settings
    from google import genai
    from google.genai import types

    job_title = params.get("job_title", "")
    description = params.get("description", "")

    if not job_title and not description:
        return {
            "success": False,
            "message": "Please provide a job title or description so I can suggest relevant skills.",
            "data": {},
            "action": "suggest_skills",
        }

    context_parts = []
    if job_title:
        context_parts.append(f"Job title: {job_title}")
    if description:
        context_parts.append(f"Description: {description[:1000]}")

    prompt = (
        f"Based on the following job context, suggest 10-15 relevant skills "
        f"(technical and soft skills) that a candidate should highlight. "
        f"Return them as a JSON array of strings. Only return the JSON array, nothing else.\n\n"
        f"{chr(10).join(context_parts)}"
    )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        raw = response.text.strip()
        # Try to parse as JSON array
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        skills = json.loads(raw)
        if not isinstance(skills, list):
            skills = [str(s) for s in skills]
    except Exception as e:
        logger.error("Skill suggestion error: %s", e)
        return {
            "success": False,
            "message": "Failed to generate skill suggestions. Please try again.",
            "data": {},
            "action": "suggest_skills",
        }

    return {
        "success": True,
        "message": f"Here are {len(skills)} suggested skills:",
        "data": {
            "skills": skills,
            "job_title": job_title,
        },
        "action": "suggest_skills",
    }
